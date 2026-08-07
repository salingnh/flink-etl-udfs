"""Financial interchange identifiers: IBAN, BIC/SWIFT and ISO 20022 message types."""

from __future__ import annotations

import re
from typing import Optional

from flink_etl_udfs.core.common import normalize_null_token_value


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


def normalize_bic_value(value: Optional[str]) -> Optional[str]:
    """Normalize an 8- or 11-character BIC/SWIFT code to uppercase; invalid shapes return ``None``."""
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    bic = re.sub(r"\s+", "", candidate).upper()
    return bic if re.fullmatch(r"[A-Z]{6}[A-Z0-9]{2}(?:[A-Z0-9]{3})?", bic) else None


def normalize_iso20022_message_type_value(value: Optional[str]) -> Optional[str]:
    """Normalize an ISO 20022 message identifier such as ``pacs.008.001.08`` to lowercase dotted form."""
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    candidate = candidate.casefold().replace("_", ".")
    return candidate if re.fullmatch(r"[a-z]{4}\.\d{3}\.\d{3}\.\d{2}", candidate) else None


__all__ = ["normalize_bic_value", "normalize_iban_value", "normalize_iso20022_message_type_value"]
