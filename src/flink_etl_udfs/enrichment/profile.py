"""HTTP enrichment client for extracting canonical social/profile source metadata."""

from __future__ import annotations

import asyncio
import json
import os
from typing import Any, Optional
from urllib import error, parse, request

DEFAULT_PROFILE_EXTRACT_ENDPOINT = (
    "http://10.9.3.70:31263/api/scrap-command/v1/Scrap/ExtractSource"
)
PROFILE_EXTRACT_ENDPOINT_ENV = "FLINK_ETL_PROFILE_EXTRACT_ENDPOINT"
PROFILE_EXTRACT_TIMEOUT_ENV = "FLINK_ETL_PROFILE_EXTRACT_TIMEOUT_SECONDS"
_DEFAULT_TIMEOUT_SECONDS = 10.0


class ProfileExtractError(RuntimeError):
    """Raised when the profile-extraction service cannot provide a valid response."""


# Kiểm tra URL profile đầu vào trước khi gửi sang dịch vụ enrichment nội bộ.
def _normalize_profile_url(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    candidate = value.strip()
    if not candidate:
        return None
    parts = parse.urlsplit(candidate)
    if parts.scheme.lower() not in {"http", "https"} or not parts.hostname:
        return None
    return candidate


# Resolve endpoint từ biến môi trường để cluster có thể thay đổi địa chỉ service mà không build lại wheel.
def _profile_extract_endpoint() -> str:
    endpoint = os.getenv(PROFILE_EXTRACT_ENDPOINT_ENV, DEFAULT_PROFILE_EXTRACT_ENDPOINT).strip()
    parts = parse.urlsplit(endpoint)
    if parts.scheme.lower() not in {"http", "https"} or not parts.hostname:
        raise ProfileExtractError(
            f"invalid profile extract endpoint configured in {PROFILE_EXTRACT_ENDPOINT_ENV}"
        )
    return endpoint


# Resolve timeout từ environment; cấu hình sai được fail-fast thay vì âm thầm dùng giá trị khác.
def _profile_extract_timeout_seconds() -> float:
    raw = os.getenv(PROFILE_EXTRACT_TIMEOUT_ENV)
    if raw is None:
        return _DEFAULT_TIMEOUT_SECONDS
    try:
        timeout = float(raw)
    except ValueError as exc:
        raise ProfileExtractError(
            f"{PROFILE_EXTRACT_TIMEOUT_ENV} must be a positive number"
        ) from exc
    if timeout <= 0:
        raise ProfileExtractError(f"{PROFILE_EXTRACT_TIMEOUT_ENV} must be greater than zero")
    return timeout


# Gọi đồng bộ API ExtractSource; hàm này được chạy trong thread bởi async wrapper phía dưới.
def extract_profile_url_sync(
    profile_url: Optional[str],
    *,
    endpoint: Optional[str] = None,
    timeout_seconds: Optional[float] = None,
) -> Optional[str]:
    """Call the profile-extraction API and return the first result object as compact JSON.

    Invalid/blank profile URLs return ``None`` without making a request. Transport errors,
    non-success service responses, and malformed response payloads raise ``ProfileExtractError``
    so the surrounding Flink async runtime can apply timeout/retry policy instead of silently
    turning infrastructure failures into missing data.
    """
    normalized_url = _normalize_profile_url(profile_url)
    if normalized_url is None:
        return None

    target = endpoint.strip() if endpoint is not None else _profile_extract_endpoint()
    target_parts = parse.urlsplit(target)
    if target_parts.scheme.lower() not in {"http", "https"} or not target_parts.hostname:
        raise ProfileExtractError("profile extract endpoint must be a valid HTTP(S) URL")

    timeout = timeout_seconds if timeout_seconds is not None else _profile_extract_timeout_seconds()
    if timeout <= 0:
        raise ProfileExtractError("timeout_seconds must be greater than zero")

    payload = json.dumps(
        {
            "parse_only": False,
            "parse_display_name": False,
            "sources": [normalized_url],
        },
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")

    http_request = request.Request(
        target,
        data=payload,
        method="POST",
        headers={
            "Accept": "text/plain",
            "Content-Type": "application/json-patch+json",
        },
    )

    try:
        with request.urlopen(http_request, timeout=timeout) as response:
            http_status = response.getcode()
            raw_body = response.read()
    except error.HTTPError as exc:
        raise ProfileExtractError(f"profile extract HTTP error: {exc.code}") from exc
    except (error.URLError, TimeoutError, OSError) as exc:
        raise ProfileExtractError(f"profile extract request failed: {exc}") from exc

    if http_status != 200:
        raise ProfileExtractError(f"profile extract HTTP status was {http_status}, expected 200")

    try:
        body: Any = json.loads(raw_body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProfileExtractError("profile extract response is not valid UTF-8 JSON") from exc

    if not isinstance(body, dict):
        raise ProfileExtractError("profile extract response must be a JSON object")
    if body.get("statusCode") != 200:
        raise ProfileExtractError(
            f"profile extract service statusCode was {body.get('statusCode')!r}, expected 200"
        )

    results = body.get("result")
    if results in (None, []):
        return None
    if not isinstance(results, list) or not isinstance(results[0], dict):
        raise ProfileExtractError("profile extract result must be a list of JSON objects")

    return json.dumps(results[0], ensure_ascii=False, sort_keys=True, separators=(",", ":"))


# Async entrypoint dùng asyncio.to_thread để không block tuần tự Python async UDF khi HTTP client là stdlib sync.
async def extract_profile_url_value(profile_url: Optional[str]) -> Optional[str]:
    """Asynchronously extract normalized profile metadata for one HTTP(S) profile URL."""
    return await asyncio.to_thread(extract_profile_url_sync, profile_url)


__all__ = [
    "DEFAULT_PROFILE_EXTRACT_ENDPOINT",
    "PROFILE_EXTRACT_ENDPOINT_ENV",
    "PROFILE_EXTRACT_TIMEOUT_ENV",
    "ProfileExtractError",
    "extract_profile_url_sync",
    "extract_profile_url_value",
]
