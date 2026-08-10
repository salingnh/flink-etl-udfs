"""Financial and legal-entity interchange identifiers."""

from __future__ import annotations

import re
from typing import Optional

from flink_etl_udfs.core.common import normalize_null_token_value


# Chuẩn hóa và kiểm tra IBAN theo ISO 13616 mod-97.
def normalize_iban_value(value: Optional[str]) -> Optional[str]:
    """Normalize and validate an IBAN using the ISO 13616 mod-97 check."""
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    iban = re.sub(r"\s+", "", candidate).upper()
    if not re.fullmatch(r"[A-Z]{2}\d{2}[A-Z0-9]{11,30}", iban):
        return None
    rearranged = iban[4:] + iban[:4]
    numeric = "".join(str(ord(ch) - 55) if ch.isalpha() else ch for ch in rearranged)
    remainder = 0
    for digit in numeric:
        remainder = (remainder * 10 + int(digit)) % 97
    return iban if remainder == 1 else None


# Chuẩn hóa BIC/SWIFT theo cấu trúc ISO 9362.
def normalize_bic_value(value: Optional[str]) -> Optional[str]:
    """Normalize an 8- or 11-character BIC/SWIFT code to uppercase."""
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    bic = re.sub(r"\s+", "", candidate).upper()
    return bic if re.fullmatch(r"[A-Z]{6}[A-Z0-9]{2}(?:[A-Z0-9]{3})?", bic) else None


# Chuẩn hóa ISO 20022 message identifier về lowercase dotted form.
def normalize_iso20022_message_type_value(value: Optional[str]) -> Optional[str]:
    """Normalize an ISO 20022 message identifier such as ``pacs.008.001.08``."""
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    candidate = candidate.casefold().replace("_", ".")
    return candidate if re.fullmatch(r"[a-z]{4}\.\d{3}\.\d{3}\.\d{2}", candidate) else None


# Chuẩn hóa và kiểm tra Legal Entity Identifier theo ISO 17442 mod-97.
def normalize_lei_value(value: Optional[str]) -> Optional[str]:
    """Normalize and validate a Legal Entity Identifier using ISO 17442 mod-97 rules."""
    if value is None:
        return None
    candidate = "".join(ch for ch in value.strip().upper() if not ch.isspace())
    if len(candidate) != 20 or not candidate.isalnum():
        return None
    numeric = "".join(str(ord(ch) - 55) if ch.isalpha() else ch for ch in candidate)
    try:
        valid = int(numeric) % 97 == 1
    except ValueError:
        return None
    return candidate if valid else None


__all__ = [
    "normalize_bic_value",
    "normalize_iban_value",
    "normalize_iso20022_message_type_value",
    "normalize_lei_value",
]
