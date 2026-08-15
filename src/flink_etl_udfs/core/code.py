"""Source-code repository and Git object identifier transformations."""

from __future__ import annotations

import re
from typing import Optional
from urllib.parse import urlsplit, urlunsplit

from flink_etl_udfs.core.internet import canonicalize_url_value, normalize_domain_value

_GIT_OBJECT_RE = re.compile(r"^[0-9a-fA-F]+$")
_SCP_REMOTE_RE = re.compile(r"^(?:(?P<user>[^@/:\s]+)@)?(?P<host>[^:/\s]+):(?P<path>[^\s]+)$")


def _strip_git_suffix(path: str) -> str:
    normalized = path.rstrip("/")
    if normalized.casefold().endswith(".git"):
        normalized = normalized[:-4]
    return normalized or "/"


# Chuẩn hóa repository URL và các Git remote representation phổ biến.
def normalize_repository_url_value(value: Optional[str]) -> Optional[str]:
    """TRY_PARSE HTTP(S), SSH, git:// and SCP-like Git remote representations."""
    if value is None:
        return None
    candidate = value.strip()
    if not candidate or any(ch.isspace() for ch in candidate):
        return None

    scp_match = _SCP_REMOTE_RE.fullmatch(candidate) if "://" not in candidate else None
    if scp_match:
        user = scp_match.group("user") or "git"
        host = normalize_domain_value(scp_match.group("host"))
        path = _strip_git_suffix("/" + scp_match.group("path").lstrip("/"))
        if host is None or path == "/":
            return None
        return urlunsplit(("ssh", f"{user}@{host}", path, "", ""))

    if candidate.casefold().startswith(("ssh://", "git://")):
        try:
            parts = urlsplit(candidate)
            if not parts.hostname:
                return None
            host = normalize_domain_value(parts.hostname)
            if host is None:
                return None
            userinfo = f"{parts.username}@" if parts.username else ""
            port = f":{parts.port}" if parts.port is not None else ""
            path = _strip_git_suffix(parts.path)
            if path == "/":
                return None
            return urlunsplit((parts.scheme.lower(), f"{userinfo}{host}{port}", path, "", ""))
        except ValueError:
            return None

    canonical = canonicalize_url_value(candidate)
    if canonical is None:
        return None
    parts = urlsplit(canonical)
    path = _strip_git_suffix(parts.path)
    return urlunsplit((parts.scheme, parts.netloc, path, "", ""))


# Chuẩn hóa full Git object ID; không nhận abbreviated hash để tránh collision giữa repo.
def normalize_git_object_id_value(value: Optional[str]) -> Optional[str]:
    """Normalize a full Git SHA-1 or SHA-256 object identifier."""
    if value is None:
        return None
    candidate = value.strip().lower()
    if len(candidate) not in {40, 64} or not _GIT_OBJECT_RE.fullmatch(candidate):
        return None
    return candidate


# Phân loại Git object ID đầy đủ là SHA-1 hay SHA-256.
def classify_git_object_hash_value(value: Optional[str]) -> Optional[str]:
    """Classify a full Git object identifier as SHA-1 or SHA-256."""
    normalized = normalize_git_object_id_value(value)
    if normalized is None:
        return None
    return "sha1" if len(normalized) == 40 else "sha256"


__all__ = [
    "classify_git_object_hash_value",
    "normalize_git_object_id_value",
    "normalize_repository_url_value",
]
