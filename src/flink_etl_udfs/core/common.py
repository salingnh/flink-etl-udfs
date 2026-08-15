"""Common deterministic ETL transforms shared across domains."""

from __future__ import annotations

import hashlib
import json
import math
import re
import unicodedata
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any, Optional

_NULL_TOKENS = {"", "null", "none", "nil", "n/a", "na", "undefined", "[null]"}
_CURRENCY_RE = re.compile(r"^[A-Z]{3}$")
_COUNTRY_CODE_RE = re.compile(r"^\+?[1-9]\d{0,2}$")
_GENERIC_CODE_RE = re.compile(r"^[A-Z0-9._/-]+$")


# Chuẩn hóa giá trị NULL dạng text thường gặp trong dữ liệu nguồn.
def normalize_null_token_value(value: Optional[str]) -> Optional[str]:
    """Trim a string and map common textual null markers to ``None``."""
    if value is None:
        return None
    candidate = value.strip()
    if candidate.casefold() in _NULL_TOKENS:
        return None
    return candidate


def _build_date(year: int, month: int, day: int) -> Optional[date]:
    try:
        return date(year, month, day)
    except ValueError:
        return None


def _try_parse_date_text(candidate: str) -> Optional[date]:
    """Parse supported deterministic date representations without locale guessing."""
    try:
        return date.fromisoformat(candidate)
    except ValueError:
        pass

    compact = re.fullmatch(r"(\d{4})(\d{2})(\d{2})", candidate)
    if compact:
        return _build_date(*(int(part) for part in compact.groups()))

    ymd = re.fullmatch(r"(\d{4})[./-](\d{1,2})[./-](\d{1,2})", candidate)
    if ymd:
        return _build_date(*(int(part) for part in ymd.groups()))

    trailing_year = re.fullmatch(r"(\d{1,2})[./-](\d{1,2})[./-](\d{4})", candidate)
    if trailing_year:
        first, second, year = (int(part) for part in trailing_year.groups())
        if first > 12 and second <= 12:
            return _build_date(year, second, first)
        if second > 12 and first <= 12:
            return _build_date(year, first, second)
        # Both <= 12 means DMY and MDY are both plausible, so do not guess.
        return None

    normalized_words = re.sub(r"\s+", " ", candidate.strip())
    for pattern in ("%d %b %Y", "%d %B %Y", "%b %d %Y", "%B %d %Y"):
        try:
            return datetime.strptime(normalized_words, pattern).date()
        except ValueError:
            continue
    return None


# Chuẩn hóa timestamp ISO 8601 có timezone về UTC để so sánh và join ổn định.
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


# Chuẩn hóa ngày từ các representation xác định được an toàn sang ISO 8601 YYYY-MM-DD.
def normalize_date_value(value: Optional[str]) -> Optional[str]:
    """TRY_PARSE supported date representations and emit canonical ``YYYY-MM-DD``.

    The function accepts deterministic alternate forms such as ``15/08/2026`` or
    ``20260815``. Ambiguous numeric forms such as ``01/02/2026`` return ``None``
    rather than guessing between DMY and MDY.
    """
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    parsed = _try_parse_date_text(candidate)
    return parsed.isoformat() if parsed is not None else None


# Chuẩn hóa số thập phân bằng Decimal, tránh sai số binary floating-point.
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


# Chuẩn hóa giá trị phần trăm theo miền 0..100 mà không làm tròn bằng float.
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


# Chuẩn hóa hình thức mã tiền tệ 3 chữ cái theo cấu trúc ISO 4217.
def normalize_currency_code_value(value: Optional[str]) -> Optional[str]:
    """Normalize a three-letter ISO-4217-shaped currency code to uppercase.

    Membership in the current ISO 4217 list should be checked against maintained
    reference data rather than hard-coded into a scalar UDF.
    """
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    candidate = candidate.upper()
    return candidate if _CURRENCY_RE.fullmatch(candidate) else None


# Chuẩn hóa số điện thoại về hình thức quốc tế E.164 khi đã biết mã quốc gia mặc định.
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


# Chuẩn hóa tên người theo Unicode NFC và khoảng trắng, không đoán cách viết hoa.
def normalize_person_name_value(value: Optional[str]) -> Optional[str]:
    """Normalize a person name using Unicode NFC and whitespace normalization.

    The transform preserves user-supplied letter case and does not assume a
    country-specific family-name/given-name order.
    """
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    normalized = unicodedata.normalize("NFC", candidate)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized or None


# Tạo khóa search/blocking cho tên Latin; không dùng làm định danh chính thức.
def latin_name_search_key_value(value: Optional[str]) -> Optional[str]:
    """Build an accent-insensitive search/blocking key for Latin-script names.

    This is intended for candidate generation in entity resolution, not as a
    canonical identity assertion. Non-Latin names require a separate strategy.
    """
    normalized = normalize_person_name_value(value)
    if normalized is None:
        return None
    normalized = normalized.replace("Đ", "D").replace("đ", "d")
    decomposed = unicodedata.normalize("NFD", normalized)
    asciiish = "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")
    tokens = re.findall(r"[0-9A-Za-z]+", asciiish.casefold())
    return " ".join(tokens) or None


# Chuẩn hóa mã định danh nghiệp vụ dạng text, không gắn với dataset cụ thể.
def normalize_identifier_code_value(value: Optional[str]) -> Optional[str]:
    """Normalize a generic business identifier to compact uppercase code syntax.

    Whitespace is removed and only ``A-Z``, digits, dot, underscore, slash and
    hyphen are valid. Registry membership remains domain-specific.
    """
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    compact = re.sub(r"\s+", "", candidate).upper()
    return compact if _GENERIC_CODE_RE.fullmatch(compact) else None


# Chuẩn hóa địa chỉ text trước bước parse/geocode/reference lookup.
def normalize_address_text_value(value: Optional[str]) -> Optional[str]:
    """Normalize free-text address Unicode, whitespace and common separators.

    The function does not infer province/district codes, postal codes or geocodes;
    those belong in authoritative reference-data enrichment.
    """
    candidate = normalize_person_name_value(value)
    if candidate is None:
        return None
    candidate = re.sub(r"\s*,\s*", ", ", candidate)
    candidate = re.sub(r"\s*;\s*", "; ", candidate)
    return candidate.strip(" ,;") or None


# Chuẩn hóa JSON thành compact representation với thứ tự key ổn định.
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


# Làm phẳng JSON lồng nhau thành dotted/indexed paths.
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


# Kiểm tra payload text có parse được thành JSON hay không.
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


# Kiểm tra trường dữ liệu có giá trị thực thay vì NULL/blank/null-token.
def quality_is_present_value(value: Optional[str]) -> bool:
    """Return true when a value is not null/blank/common null token."""
    return normalize_null_token_value(value) is not None


# Kiểm tra giá trị số có nằm trong khoảng min/max khai báo hay không.
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


# Tạo record ID ổn định từ nguồn và natural key để deduplicate/idempotent load.
def stable_record_id_value(source: Optional[str], natural_key: Optional[str]) -> Optional[str]:
    """Build a deterministic record identifier from provenance and a natural key."""
    source_norm = normalize_null_token_value(source)
    key_norm = normalize_null_token_value(natural_key)
    if source_norm is None or key_norm is None:
        return None
    payload = f"{source_norm}\x1f{key_norm}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


# Chuẩn hóa score xác suất về miền 0..1 và loại NaN/Infinity/out-of-range.
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
    "latin_name_search_key_value",
    "normalize_address_text_value",
    "normalize_currency_code_value",
    "normalize_date_value",
    "normalize_decimal_value",
    "normalize_e164_value",
    "normalize_identifier_code_value",
    "normalize_iso_datetime_value",
    "normalize_null_token_value",
    "normalize_percentage_value",
    "normalize_person_name_value",
    "normalize_probability_value",
    "quality_is_present_value",
    "quality_number_in_range_value",
    "stable_record_id_value",
]
