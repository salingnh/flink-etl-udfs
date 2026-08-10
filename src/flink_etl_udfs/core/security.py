"""Generic security identifier and IOC normalization transformations."""

from __future__ import annotations

import re
from typing import Optional

_HEX_RE = re.compile(r"^[0-9a-fA-F]+$")
_CVE_RE = re.compile(r"^CVE[-_ ]?(\d{4})[-_ ]?(\d{4,})$", flags=re.IGNORECASE)
_HASH_LENGTH_TYPES = {32: "md5", 40: "sha1", 64: "sha256", 128: "sha512"}


# Chuẩn hóa digest hex phổ biến về lowercase và chỉ nhận độ dài MD5/SHA-1/SHA-256/SHA-512.
def normalize_hex_hash_value(value: Optional[str]) -> Optional[str]:
    """Normalize a well-known hexadecimal digest while rejecting unknown lengths."""
    if value is None:
        return None
    candidate = value.strip().lower()
    if len(candidate) not in _HASH_LENGTH_TYPES or not _HEX_RE.fullmatch(candidate):
        return None
    return candidate


# Phân loại digest đã chuẩn hóa theo họ MD5/SHA dựa trên độ dài chuẩn.
def classify_hash_type_value(value: Optional[str]) -> Optional[str]:
    """Classify a normalized hexadecimal digest by length."""
    normalized = normalize_hex_hash_value(value)
    if normalized is None:
        return None
    return _HASH_LENGTH_TYPES[len(normalized)]


# Chuẩn hóa CVE identifier về dạng CVE-YYYY-NNNN... để join và deduplicate ổn định.
def normalize_cve_value(value: Optional[str]) -> Optional[str]:
    """Normalize a CVE identifier to CVE-YYYY-NNNN... form."""
    if value is None:
        return None
    match = _CVE_RE.fullmatch(value.strip())
    if match is None:
        return None
    year, number = match.groups()
    return f"CVE-{year}-{number}"


__all__ = ["classify_hash_type_value", "normalize_cve_value", "normalize_hex_hash_value"]
