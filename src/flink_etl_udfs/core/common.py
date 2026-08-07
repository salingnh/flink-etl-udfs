"""Common deterministic ETL transforms shared across domains."""

from __future__ import annotations

import hashlib
import json
import math
import re
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any, Optional

_NULL_TOKENS = {"", "null", "none", "nil", "n/a", "na", "undefined", "[null]"}
_CURRENCY_RE = re.compile(r"^[A-Z]{3}$")
_COUNTRY_CODE_RE = re.compile(r"^\+?[1-9]\d{0,2}$")


def normalize_null_token_value(value: Optional[str]) -> Optional[str]:
    """Trim a string and map common textual null markers to ``None``."""
    if value is None:
        return None
    candidate = value.strip()
    if candidate.casefold() in _NULL_TOKENS:
        return None
    return candidate


def normalize_iso_datetime_value(value: Optional[str]) -> Optional[str]:
    """Normalize an ISO-8601 timestamp to UTC with a ``Z`` suffix.

    Naive timestamps are deliberately rejected because guessing a timezone in a
    generic UDF creates silent time shifts.
    """
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    try:
        parsed = datetime.fromisoformat(candidate.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def normalize_date_value(value: Optional[str]) -> Optional[str]:
    """Normalize an ISO date to ``YYYY-MM-DD``."""
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    try:
        return date.fromisoformat(candidate).isoformat()
    except ValueError:
        return None


def normalize_decimal_value(value: Optional[str]) -> Optional[str]:
    """Normalize a decimal number without introducing binary floating-point error."""
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    candidate = candidate.replace("_", "").replace(" ", "")
    try:
        number = Decimal(candidate)
    except InvalidOperation:
        return None
    if not number.is_finite():
        return None
    normalized = format(number.normalize(), "f")
    if "." in normalized:
        normalized = normalized.rstrip("0").rstrip(".")
    if normalized in {"-0", ""}:
        return "0"
    return normalized


def normalize_percentage_value(value: Optional[str]) -> Optional[str]:
    """Normalize a percentage in the inclusive range 0..100 as exact decimal text."""
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    if candidate.endswith("%"):
        candidate = candidate[:-1].strip()
    normalized = normalize_decimal_value(candidate)
    if normalized is None:
        return None
    number = Decimal(normalized)
    if number < 0 or number > 100:
        return None
    return normalized


def normalize_currency_code_value(value: Optional[str]) -> Optional[str]:
    """Normalize a three-letter currency code shape (for example ``VND``)."""
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    candidate = candidate.upper()
    return candidate if _CURRENCY_RE.fullmatch(candidate) else None


def normalize_e164_value(value: Optional[str], default_country_code: Optional[str]) -> Optional[str]:
    """Perform conservative E.164-shape normalization without carrier lookup.

    ``default_country_code`` is used only for national numbers that begin with a
    single ``0``. Full country-specific validation belongs in a domain profile or
    libphonenumber-backed enrichment layer.
    """
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    digits = "".join(ch for ch in candidate if ch.isascii() and ch.isdigit())
    if not digits:
        return None

    if candidate.lstrip().startswith("+"):
        international = digits
    elif digits.startswith("00"):
        international = digits[2:]
    elif default_country_code:
        code = default_country_code.strip()
        if not _COUNTRY_CODE_RE.fullmatch(code):
            return None
        code_digits = code.lstrip("+")
        if digits.startswith("0") and not digits.startswith("00"):
            international = code_digits + digits[1:]
        elif digits.startswith(code_digits):
            international = digits
        else:
            return None
    else:
        return None

    if not (7 <= len(international) <= 15) or international.startswith("0"):
        return None
    return "+" + international


def canonicalize_json_value(value: Optional[str]) -> Optional[str]:
    """Return canonical compact JSON with sorted object keys."""
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    try:
        parsed = json.loads(candidate)
    except (json.JSONDecodeError, TypeError):
        return None
    return json.dumps(parsed, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _flatten_json(obj: Any, prefix: str, output: dict[str, Any]) -> None:
    if isinstance(obj, dict):
        for key in sorted(obj):
            child = f"{prefix}.{key}" if prefix else str(key)
            _flatten_json(obj[key], child, output)
    elif isinstance(obj, list):
        for index, item in enumerate(obj):
            child = f"{prefix}[{index}]"
            _flatten_json(item, child, output)
    else:
        output[prefix or "$value"] = obj


def flatten_json_value(value: Optional[str]) -> Optional[str]:
    """Flatten nested JSON into a canonical JSON object using dotted paths."""
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    try:
        parsed = json.loads(candidate)
    except json.JSONDecodeError:
        return None
    flattened: dict[str, Any] = {}
    _flatten_json(parsed, "", flattened)
    return json.dumps(flattened, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def is_valid_json_value(value: Optional[str]) -> bool:
    """Return whether a non-null string is valid JSON."""
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return False
    try:
        json.loads(candidate)
    except json.JSONDecodeError:
        return False
    return True


def quality_is_present_value(value: Optional[str]) -> bool:
    """Return true when a value is not null/blank/common null token."""
    return normalize_null_token_value(value) is not None


def quality_number_in_range_value(
    value: Optional[str], minimum: Optional[str], maximum: Optional[str]
) -> bool:
    """Validate an exact decimal against optional inclusive bounds."""
    normalized = normalize_decimal_value(value)
    if normalized is None:
        return False
    number = Decimal(normalized)
    if minimum is not None:
        min_value = normalize_decimal_value(minimum)
        if min_value is None or number < Decimal(min_value):
            return False
    if maximum is not None:
        max_value = normalize_decimal_value(maximum)
        if max_value is None or number > Decimal(max_value):
            return False
    return True


def stable_record_id_value(source: Optional[str], natural_key: Optional[str]) -> Optional[str]:
    """Build a deterministic record identifier from provenance and a natural key."""
    source_norm = normalize_null_token_value(source)
    key_norm = normalize_null_token_value(natural_key)
    if source_norm is None or key_norm is None:
        return None
    payload = f"{source_norm}\x1f{key_norm}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def normalize_probability_value(value: Optional[str]) -> Optional[float]:
    """Normalize a finite probability in the inclusive range 0..1."""
    candidate = normalize_decimal_value(value)
    if candidate is None:
        return None
    number = float(Decimal(candidate))
    if not math.isfinite(number) or not 0.0 <= number <= 1.0:
        return None
    return number


__all__ = [
    "canonicalize_json_value",
    "flatten_json_value",
    "is_valid_json_value",
    "normalize_currency_code_value",
    "normalize_date_value",
    "normalize_decimal_value",
    "normalize_e164_value",
    "normalize_iso_datetime_value",
    "normalize_null_token_value",
    "normalize_percentage_value",
    "normalize_probability_value",
    "quality_is_present_value",
    "quality_number_in_range_value",
    "stable_record_id_value",
]
