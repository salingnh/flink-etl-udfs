"""Financial and legal-entity interchange identifiers."""

from __future__ import annotations

import re
from typing import Optional

from flink_etl_udfs.core.common import normalize_null_token_value


def _mod97_alphanumeric(value: str) -> int:
    numeric = "".join(str(ord(ch) - 55) if ch.isalpha() else ch for ch in value)
    remainder = 0
    for digit in numeric:
        remainder = (remainder * 10 + int(digit)) % 97
    return remainder


# Chuẩn hóa và kiểm tra IBAN theo ISO 13616 mod-97.
def normalize_iban_value(value: Optional[str]) -> Optional[str]:
    """TRY_PARSE common IBAN labels/separators and validate ISO 13616 mod-97."""
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    candidate = re.sub(r"(?i)^IBAN\s*[:#-]?\s*", "", candidate)
    iban = re.sub(r"[\s-]+", "", candidate).upper()
    if not re.fullmatch(r"[A-Z]{2}\d{2}[A-Z0-9]{11,30}", iban):
        return None
    rearranged = iban[4:] + iban[:4]
    return iban if _mod97_alphanumeric(rearranged) == 1 else None


# Chuẩn hóa BIC/SWIFT theo cấu trúc ISO 9362.
def normalize_bic_value(value: Optional[str]) -> Optional[str]:
    """TRY_PARSE common BIC/SWIFT labels/separators to canonical uppercase text."""
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    candidate = re.sub(r"(?i)^(?:BIC|SWIFT(?:\s*CODE)?)\s*[:#-]?\s*", "", candidate)
    bic = re.sub(r"[\s-]+", "", candidate).upper()
    return bic if re.fullmatch(r"[A-Z]{6}[A-Z0-9]{2}(?:[A-Z0-9]{3})?", bic) else None


# Chuẩn hóa ISO 20022 message identifier về lowercase dotted form.
def normalize_iso20022_message_type_value(value: Optional[str]) -> Optional[str]:
    """TRY_PARSE message identifier aliases/namespace URNs to dotted lowercase form."""
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    lowered = candidate.casefold().strip()
    urn_prefix = "urn:iso:std:iso:20022:tech:xsd:"
    if lowered.startswith(urn_prefix):
        lowered = lowered[len(urn_prefix) :]
    lowered = re.sub(r"[\s_/-]+", ".", lowered)
    lowered = re.sub(r"\.+", ".", lowered).strip(".")
    return lowered if re.fullmatch(r"[a-z]{4}\.\d{3}\.\d{3}\.\d{2}", lowered) else None


# Chuẩn hóa và kiểm tra Legal Entity Identifier theo ISO 17442 mod-97.
def normalize_lei_value(value: Optional[str]) -> Optional[str]:
    """TRY_PARSE common LEI labels/separators and validate ISO 17442 mod-97."""
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    candidate = re.sub(r"(?i)^LEI\s*[:#-]?\s*", "", candidate)
    compact = re.sub(r"[\s-]+", "", candidate).upper()
    if len(compact) != 20 or not compact.isalnum():
        return None
    return compact if _mod97_alphanumeric(compact) == 1 else None


__all__ = [
    "normalize_bic_value",
    "normalize_iban_value",
    "normalize_iso20022_message_type_value",
    "normalize_lei_value",
]
