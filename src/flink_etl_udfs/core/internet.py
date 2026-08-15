"""Generic internet, DNS, and URL normalization transformations."""

from __future__ import annotations

import ipaddress
import re
from typing import Optional
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

_TRACKING_KEYS = {"fbclid", "gclid", "mc_cid", "mc_eid", "ref", "ref_src"}
_SENSITIVE_QUERY_KEYS = {
    "access_token",
    "api_key",
    "apikey",
    "auth",
    "authorization",
    "key",
    "password",
    "secret",
    "session",
    "sessionid",
    "token",
}
_DNS_RECORD_TYPES = {
    "A",
    "AAAA",
    "CAA",
    "CNAME",
    "DNSKEY",
    "DS",
    "HTTPS",
    "MX",
    "NAPTR",
    "NS",
    "PTR",
    "SOA",
    "SRV",
    "SVCB",
    "TLSA",
    "TXT",
}


def _valid_ascii_host(host: str) -> bool:
    if len(host) > 253:
        return False
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        pass
    labels = host.split(".")
    return all(
        1 <= len(label) <= 63
        and not label.startswith("-")
        and not label.endswith("-")
        and re.fullmatch(r"[a-z0-9-]+", label) is not None
        for label in labels
    )


def _extract_domain_candidate(value: str) -> Optional[str]:
    candidate = value.strip()
    if not candidate:
        return None

    if "://" in candidate:
        try:
            return urlsplit(candidate).hostname
        except ValueError:
            return None

    if candidate.casefold().startswith("mailto:"):
        candidate = candidate[7:].split("?", 1)[0]
    if "@" in candidate and candidate.count("@") == 1:
        candidate = candidate.rsplit("@", 1)[1]

    return candidate.strip().rstrip(".") or None


# Chuẩn hóa DNS name về lowercase IDNA ASCII để join domain ổn định.
def normalize_domain_value(value: Optional[str]) -> Optional[str]:
    """Normalize bare domain, URL host or email domain to IDNA ASCII lowercase."""
    if value is None:
        return None
    candidate = _extract_domain_candidate(value)
    if candidate is None or any(ch.isspace() for ch in candidate):
        return None
    if candidate.startswith("[") and candidate.endswith("]"):
        candidate = candidate[1:-1]
    try:
        normalized = candidate.encode("idna").decode("ascii").lower()
    except UnicodeError:
        return None
    return normalized if _valid_ascii_host(normalized) else None


def _normalize_netloc(scheme: str, hostname: str, port: Optional[int]) -> str:
    normalized_host = normalize_domain_value(hostname)
    if normalized_host is None:
        return ""
    default_port = (scheme == "http" and port == 80) or (scheme == "https" and port == 443)
    host_for_url = (
        f"[{normalized_host}]" if ":" in normalized_host and not normalized_host.startswith("[") else normalized_host
    )
    return host_for_url if port is None or default_port else f"{host_for_url}:{port}"


def _infer_http_scheme(candidate: str) -> str:
    if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*://", candidate):
        return candidate
    if any(ch.isspace() for ch in candidate):
        return candidate
    authority = candidate.split("/", 1)[0]
    host = authority.rsplit("@", 1)[-1].split(":", 1)[0].strip("[]")
    if "." in host:
        return "https://" + candidate
    try:
        ipaddress.ip_address(host)
        return "https://" + candidate
    except ValueError:
        return candidate


# Chuẩn hóa HTTP(S) URL, bỏ credentials, tracking params và fragment.
def canonicalize_url_value(value: Optional[str]) -> Optional[str]:
    """TRY_PARSE common HTTP(S) URL forms and emit a canonical URL."""
    if value is None:
        return None
    candidate = value.strip()
    if not candidate:
        return None
    candidate = _infer_http_scheme(candidate)
    try:
        parts = urlsplit(candidate)
        scheme = parts.scheme.lower()
        if scheme not in {"http", "https"} or not parts.hostname:
            return None
        netloc = _normalize_netloc(scheme, parts.hostname, parts.port)
    except ValueError:
        return None
    if not netloc:
        return None
    query_items = [
        (key, val)
        for key, val in parse_qsl(parts.query, keep_blank_values=True)
        if not key.lower().startswith("utm_") and key.lower() not in _TRACKING_KEYS
    ]
    query_items.sort()
    query = urlencode(query_items, doseq=True)
    path = parts.path or "/"
    return urlunsplit((scheme, netloc, path, query, ""))


# Trích hostname canonical từ HTTP(S) URL.
def extract_url_host_value(value: Optional[str]) -> Optional[str]:
    """Extract the normalized hostname from an HTTP(S) URL."""
    canonical = canonicalize_url_value(value)
    if canonical is None:
        return None
    return urlsplit(canonical).hostname


# Xóa userinfo và che query parameter thường chứa secret trước khi lưu/log.
def redact_url_secrets_value(value: Optional[str]) -> Optional[str]:
    """Remove URL userinfo and redact values of common secret-bearing query keys."""
    if value is None:
        return None
    candidate = value.strip()
    if not candidate:
        return None
    candidate = _infer_http_scheme(candidate)
    try:
        parts = urlsplit(candidate)
        scheme = parts.scheme.lower()
        if scheme not in {"http", "https"} or not parts.hostname:
            return None
        netloc = _normalize_netloc(scheme, parts.hostname, parts.port)
    except ValueError:
        return None
    if not netloc:
        return None
    query_items = [
        (key, "[REDACTED]" if key.lower() in _SENSITIVE_QUERY_KEYS else val)
        for key, val in parse_qsl(parts.query, keep_blank_values=True)
    ]
    query = urlencode(query_items, doseq=True)
    path = parts.path or "/"
    return urlunsplit((scheme, netloc, path, query, ""))


# Chuẩn hóa Autonomous System Number về AS<number> theo miền 32-bit.
def normalize_asn_value(value: Optional[str]) -> Optional[str]:
    """Normalize a 32-bit Autonomous System Number to AS<number> form."""
    if value is None:
        return None
    candidate = value.strip().upper()
    if candidate.startswith("AS"):
        candidate = candidate[2:]
    if not candidate.isdigit():
        return None
    number = int(candidate)
    if not 0 <= number <= 4_294_967_295:
        return None
    return f"AS{number}"


# Chuẩn hóa DNS resource-record type phổ biến về uppercase.
def normalize_dns_record_type_value(value: Optional[str]) -> Optional[str]:
    """Normalize a common DNS resource-record type to uppercase."""
    if value is None:
        return None
    candidate = value.strip().upper()
    return candidate if candidate in _DNS_RECORD_TYPES else None


# Chuẩn hóa MIME media type về lowercase và bỏ parameters như charset.
def normalize_mime_type_value(value: Optional[str]) -> Optional[str]:
    """Normalize a MIME media type while dropping optional parameters."""
    if value is None:
        return None
    media_type = value.split(";", 1)[0].strip().lower()
    if media_type.count("/") != 1:
        return None
    major, minor = media_type.split("/", 1)
    if not major or not minor or any(ch.isspace() for ch in media_type):
        return None
    return media_type


__all__ = [
    "canonicalize_url_value",
    "extract_url_host_value",
    "normalize_asn_value",
    "normalize_dns_record_type_value",
    "normalize_domain_value",
    "normalize_mime_type_value",
    "redact_url_secrets_value",
]
