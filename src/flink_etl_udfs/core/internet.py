"""Generic internet, DNS, and URL normalization transformations."""

from __future__ import annotations

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


# Chuẩn hóa DNS name về lowercase IDNA ASCII để join domain ổn định.
def normalize_domain_value(value: Optional[str]) -> Optional[str]:
    """Normalize a DNS name using IDNA ASCII representation and lowercase form."""
    if value is None:
        return None
    candidate = value.strip().rstrip(".")
    if not candidate:
        return None
    try:
        return candidate.encode("idna").decode("ascii").lower()
    except UnicodeError:
        return None


def _normalize_netloc(scheme: str, hostname: str, port: Optional[int]) -> str:
    normalized_host = normalize_domain_value(hostname)
    if normalized_host is None:
        return ""
    default_port = (scheme == "http" and port == 80) or (scheme == "https" and port == 443)
    return normalized_host if port is None or default_port else f"{normalized_host}:{port}"


# Chuẩn hóa HTTP(S) URL, bỏ credentials, tracking params và fragment.
def canonicalize_url_value(value: Optional[str]) -> Optional[str]:
    """Canonicalize HTTP(S), remove credentials, tracking parameters, and fragments."""
    if value is None:
        return None
    candidate = value.strip()
    if not candidate:
        return None
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
