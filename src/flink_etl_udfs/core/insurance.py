"""Insurance/ACORD-oriented scalar normalization helpers."""

from __future__ import annotations

import re
from typing import Optional

from flink_etl_udfs.core.common import normalize_null_token_value


def normalize_acord_version_value(value: Optional[str]) -> Optional[str]:
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    candidate = candidate.upper().replace(" ", "")
    candidate = candidate.removeprefix("ACORD")
    candidate = candidate.lstrip("-_V")
    return candidate if re.fullmatch(r"\d{1,4}(?:\.\d{1,4}){0,2}", candidate) else None


def normalize_policy_number_value(value: Optional[str]) -> Optional[str]:
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    candidate = re.sub(r"\s+", "", candidate).upper()
    return candidate if re.fullmatch(r"[A-Z0-9][A-Z0-9./_-]{2,63}", candidate) else None


def normalize_coverage_code_value(value: Optional[str]) -> Optional[str]:
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    candidate = re.sub(r"\s+", "_", candidate).upper()
    return candidate if re.fullmatch(r"[A-Z0-9][A-Z0-9_-]{0,31}", candidate) else None


__all__ = [
    "normalize_acord_version_value",
    "normalize_coverage_code_value",
    "normalize_policy_number_value",
]
