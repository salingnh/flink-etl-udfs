"""Generic security identifier and IOC normalization transformations."""

from __future__ import annotations

import re
from typing import Optional

_HEX_RE = re.compile(r"^[0-9a-fA-F]+$")
_HASH_LENGTH_TYPES = {32: "md5", 40: "sha1", 64: "sha256", 128: "sha512"}
_HASH_PREFIX_LENGTHS = {"md5": 32, "sha1": 40, "sha256": 64, "sha512": 128}


def _normalize_hash_prefix(value: str) -> tuple[Optional[str], str]:
    match = re.fullmatch(r"(?i)(md5|sha-?1|sha-?256|sha-?512)\s*[:=]\s*(.+)", value)
    if not match:
        return None, value
    algorithm, payload = match.groups()
    return algorithm.casefold().replace("-", ""), payload


# Chuẩn hóa digest hex phổ biến về lowercase và chỉ nhận độ dài MD5/SHA-1/SHA-256/SHA-512.
def normalize_hex_hash_value(value: Optional[str]) -> Optional[str]:
    """TRY_PARSE common prefixed/separated hexadecimal digest representations."""
    if value is None:
        return None
    algorithm, payload = _normalize_hash_prefix(value.strip())
    candidate = re.sub(r"[\s:-]+", "", payload).lower()
    if len(candidate) not in _HASH_LENGTH_TYPES or not _HEX_RE.fullmatch(candidate):
        return None
    if algorithm is not None and _HASH_PREFIX_LENGTHS[algorithm] != len(candidate):
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
    """TRY_PARSE common CVE separators/prefix forms to ``CVE-YYYY-NNNN...``."""
    if value is None:
        return None
    candidate = value.strip()
    candidate = re.sub(r"(?i)^CVE\s*[:#]?\s*", "", candidate)
    match = re.fullmatch(r"(\d{4})\s*[-_: /]\s*(\d{4,})", candidate)
    if match is None:
        return None
    year, number = match.groups()
    return f"CVE-{year}-{number}"


__all__ = ["classify_hash_type_value", "normalize_cve_value", "normalize_hex_hash_value"]
