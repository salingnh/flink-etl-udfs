"""Vietnam-specific deterministic normalization helpers."""

from __future__ import annotations

import re
import unicodedata
from typing import Optional

from flink_etl_udfs.core.common import normalize_e164_value, normalize_null_token_value
from flink_etl_udfs.core.text import normalize_unicode_nfc_value, normalize_whitespace_value

_VN_CITIZEN_RE = re.compile(r"^(?:\d{9}|\d{12})$")
_VN_TAX_RE = re.compile(r"^(\d{10})(?:-?(\d{3}))?$")
_VN_CODE_RE = re.compile(r"^[A-Z0-9._/-]+$")


def normalize_vn_citizen_id_value(value: Optional[str]) -> Optional[str]:
    """Normalize Vietnamese CMND/CCCD shape while preserving leading zeroes."""
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    digits = "".join(ch for ch in candidate if ch.isascii() and ch.isdigit())
    return digits if _VN_CITIZEN_RE.fullmatch(digits) else None


def classify_vn_identity_id_value(value: Optional[str]) -> Optional[str]:
    """Classify a normalized 9-digit CMND or 12-digit CCCD by length only."""
    normalized = normalize_vn_citizen_id_value(value)
    if normalized is None:
        return None
    return "cmnd_9" if len(normalized) == 9 else "cccd_12"


def normalize_vn_tax_id_value(value: Optional[str]) -> Optional[str]:
    """Normalize Vietnamese tax identifiers to ``10digits`` or ``10digits-3digits``.

    This validates the structural format only; checksum/business-registry validation
    should be performed against an authoritative source.
    """
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    compact = re.sub(r"\s+", "", candidate)
    match = _VN_TAX_RE.fullmatch(compact)
    if not match:
        return None
    base, branch = match.groups()
    return base if branch is None else f"{base}-{branch}"


def classify_vn_tax_id_value(value: Optional[str]) -> Optional[str]:
    normalized = normalize_vn_tax_id_value(value)
    if normalized is None:
        return None
    return "enterprise" if "-" not in normalized else "dependent_unit"


def normalize_vn_phone_value(value: Optional[str]) -> Optional[str]:
    """Normalize a Vietnamese phone-number shape to E.164 using country code +84."""
    return normalize_e164_value(value, "+84")


def normalize_vn_name_value(value: Optional[str]) -> Optional[str]:
    """Normalize Vietnamese personal names without changing user-supplied case."""
    candidate = normalize_whitespace_value(normalize_unicode_nfc_value(value))
    return candidate or None


def vietnamese_name_search_key_value(value: Optional[str]) -> Optional[str]:
    """Build an accent-insensitive blocking/search key for Vietnamese names."""
    normalized = normalize_vn_name_value(value)
    if normalized is None:
        return None
    normalized = normalized.replace("Đ", "D").replace("đ", "d")
    decomposed = unicodedata.normalize("NFD", normalized)
    asciiish = "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")
    tokens = re.findall(r"[0-9A-Za-z]+", asciiish.casefold())
    return " ".join(tokens) or None


def normalize_vn_address_value(value: Optional[str]) -> Optional[str]:
    """Normalize Vietnamese free-text addresses without guessing administrative codes."""
    candidate = normalize_vn_name_value(value)
    if candidate is None:
        return None
    candidate = re.sub(r"\s*,\s*", ", ", candidate)
    candidate = re.sub(r"\s*-\s*", " - ", candidate)
    return candidate.strip(" ,-") or None


def _normalize_domain_code(value: Optional[str]) -> Optional[str]:
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    candidate = re.sub(r"\s+", "", candidate).upper()
    return candidate if _VN_CODE_RE.fullmatch(candidate) else None


def normalize_school_code_value(value: Optional[str]) -> Optional[str]:
    return _normalize_domain_code(value)


def normalize_teacher_code_value(value: Optional[str]) -> Optional[str]:
    return _normalize_domain_code(value)


def normalize_student_code_value(value: Optional[str]) -> Optional[str]:
    return _normalize_domain_code(value)


def normalize_academic_year_value(value: Optional[str]) -> Optional[str]:
    """Normalize school years such as ``2025-2026`` or ``2025/26``."""
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    match = re.fullmatch(r"(\d{4})\s*[-/]\s*(\d{2}|\d{4})", candidate)
    if not match:
        return None
    start = int(match.group(1))
    end_text = match.group(2)
    end = int(str(start)[:2] + end_text) if len(end_text) == 2 else int(end_text)
    if end != start + 1:
        return None
    return f"{start:04d}-{end:04d}"


def normalize_sms_brandname_value(value: Optional[str]) -> Optional[str]:
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    compact = re.sub(r"\s+", "", candidate).upper()
    return compact or None


def normalize_bank_account_value(value: Optional[str]) -> Optional[str]:
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    compact = re.sub(r"[\s.-]+", "", candidate)
    if not compact or not compact.isalnum():
        return None
    return compact.upper()


def build_entity_blocking_key_value(
    name: Optional[str], phone: Optional[str], email: Optional[str]
) -> Optional[str]:
    """Build a readable entity-resolution blocking key from available stable features."""
    parts: list[str] = []
    name_key = vietnamese_name_search_key_value(name)
    phone_key = normalize_vn_phone_value(phone)
    email_key = normalize_null_token_value(email)
    if name_key:
        parts.append(f"n={name_key}")
    if phone_key:
        parts.append(f"p={phone_key}")
    if email_key and "@" in email_key:
        parts.append(f"e={email_key.casefold()}")
    return "|".join(parts) or None


__all__ = [
    "build_entity_blocking_key_value",
    "classify_vn_identity_id_value",
    "classify_vn_tax_id_value",
    "normalize_academic_year_value",
    "normalize_bank_account_value",
    "normalize_school_code_value",
    "normalize_sms_brandname_value",
    "normalize_student_code_value",
    "normalize_teacher_code_value",
    "normalize_vn_address_value",
    "normalize_vn_citizen_id_value",
    "normalize_vn_name_value",
    "normalize_vn_phone_value",
    "normalize_vn_tax_id_value",
    "vietnamese_name_search_key_value",
]
