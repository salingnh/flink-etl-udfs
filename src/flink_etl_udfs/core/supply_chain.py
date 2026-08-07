"""GS1/EPCIS identifier and event normalization helpers."""

from __future__ import annotations

import re
from typing import Optional

from flink_etl_udfs.core.common import normalize_null_token_value


def _gs1_check_digit_valid(digits: str) -> bool:
    body = digits[:-1]
    check = int(digits[-1])
    total = 0
    for index, char in enumerate(reversed(body), start=1):
        total += int(char) * (3 if index % 2 == 1 else 1)
    expected = (10 - total % 10) % 10
    return check == expected


def normalize_gtin_value(value: Optional[str]) -> Optional[str]:
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    digits = re.sub(r"[\s-]+", "", candidate)
    if len(digits) not in {8, 12, 13, 14} or not digits.isdigit():
        return None
    return digits if _gs1_check_digit_valid(digits) else None


def normalize_sscc_value(value: Optional[str]) -> Optional[str]:
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    digits = re.sub(r"[\s-]+", "", candidate)
    if len(digits) != 18 or not digits.isdigit():
        return None
    return digits if _gs1_check_digit_valid(digits) else None


def normalize_epcis_event_type_value(value: Optional[str]) -> Optional[str]:
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    key = re.sub(r"[^a-z]", "", candidate.casefold())
    mapping = {
        "objectevent": "ObjectEvent",
        "aggregationevent": "AggregationEvent",
        "transactionevent": "TransactionEvent",
        "transformationevent": "TransformationEvent",
        "associationevent": "AssociationEvent",
    }
    return mapping.get(key)


__all__ = ["normalize_epcis_event_type_value", "normalize_gtin_value", "normalize_sscc_value"]
