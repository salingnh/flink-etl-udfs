"""Common deterministic ETL transforms shared across domains."""

from __future__ import annotations

import hashlib
import json
import math
import re
import unicodedata
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from typing import Any, Optional

_NULL_TOKENS = {
    "",
    "null",
    "none",
    "nil",
    "n/a",
    "na",
    "undefined",
    "[null]",
    "(null)",
    "<null>",
    "\\n",
}
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


def _parse_timezone_token(token: str) -> Optional[timezone]:
    if token.upper() == "Z":
        return timezone.utc
    match = re.fullmatch(r"([+-])(\d{2}):?(\d{2})", token)
    if not match:
        return None
    sign, hours_text, minutes_text = match.groups()
    hours = int(hours_text)
    minutes = int(minutes_text)
    if hours > 23 or minutes > 59:
        return None
    delta = timedelta(hours=hours, minutes=minutes)
    if sign == "-":
        delta = -delta
    try:
        return timezone(delta)
    except ValueError:
        return None


def _try_parse_datetime_text(candidate: str) -> Optional[datetime]:
    """Parse supported timezone-aware datetime forms without inferring a timezone."""
    iso_candidate = candidate.replace("z", "Z")
    try:
        parsed = datetime.fromisoformat(iso_candidate.replace("Z", "+00:00"))
    except ValueError:
        parsed = None
    if parsed is not None:
        return parsed if parsed.tzinfo is not None else None

    match = re.fullmatch(
        r"(.+?)[ T](\d{1,2}):(\d{2})(?::(\d{2})(?:[.,](\d{1,6}))?)?\s*(Z|[+-]\d{2}:?\d{2})",
        candidate,
        flags=re.IGNORECASE,
    )
    if not match:
        return None
    date_text, hour_text, minute_text, second_text, fraction_text, zone_text = match.groups()
    parsed_date = _try_parse_date_text(date_text.strip())
    parsed_zone = _parse_timezone_token(zone_text)
    if parsed_date is None or parsed_zone is None:
        return None
    hour = int(hour_text)
    minute = int(minute_text)
    second = int(second_text or "0")
    microsecond = int((fraction_text or "").ljust(6, "0") or "0")
    try:
        return datetime(
            parsed_date.year,
            parsed_date.month,
            parsed_date.day,
            hour,
            minute,
            second,
            microsecond,
            tzinfo=parsed_zone,
        )
    except ValueError:
        return None


# Chuẩn hóa timestamp từ các representation có timezone về UTC để so sánh/join ổn định.
def normalize_iso_datetime_value(value: Optional[str]) -> Optional[str]:
    """TRY_PARSE supported timezone-aware timestamps and emit canonical UTC text.

    Naive timestamps are deliberately rejected because guessing a timezone in a
    generic UDF creates silent time shifts. Alternate deterministic date forms are
    accepted when the date order can be resolved safely.
    """
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    parsed = _try_parse_datetime_text(candidate)
    if parsed is None:
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


def _grouped_integer_is_valid(value: str, separator: str) -> bool:
    signless = value.lstrip("+-")
    groups = signless.split(separator)
    return bool(groups) and 1 <= len(groups[0]) <= 3 and all(
        len(group) == 3 and group.isdigit() for group in groups[1:]
    ) and groups[0].isdigit()


def _normalize_decimal_candidate(candidate: str) -> Optional[str]:
    compact = re.sub(r"[\s_]", "", candidate)
    if not compact:
        return None
    if not re.fullmatch(r"[+-]?[0-9.,]+", compact):
        return None

    if "," in compact and "." in compact:
        decimal_separator = "," if compact.rfind(",") > compact.rfind(".") else "."
        grouping_separator = "." if decimal_separator == "," else ","
        integer_part, decimal_part = compact.rsplit(decimal_separator, 1)
        if not decimal_part.isdigit() or not _grouped_integer_is_valid(integer_part, grouping_separator):
            return None
        compact = integer_part.replace(grouping_separator, "") + "." + decimal_part
    elif "," in compact:
        if compact.count(",") > 1:
            if not _grouped_integer_is_valid(compact, ","):
                return None
            compact = compact.replace(",", "")
        else:
            integer_part, decimal_part = compact.split(",", 1)
            signless_integer = integer_part.lstrip("+-")
            if not signless_integer.isdigit() or not decimal_part.isdigit():
                return None
            # `1,234` could be 1234 or 1.234; refuse to guess.
            if len(decimal_part) == 3 and 1 <= len(signless_integer) <= 3:
                return None
            compact = integer_part + "." + decimal_part
    elif compact.count(".") > 1:
        if not _grouped_integer_is_valid(compact, "."):
            return None
        compact = compact.replace(".", "")

    return compact


# Chuẩn hóa số thập phân bằng Decimal, tránh sai số binary floating-point.
def normalize_decimal_value(value: Optional[str]) -> Optional[str]:
    """TRY_PARSE deterministic decimal representations to canonical decimal text."""
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    normalized_candidate = _normalize_decimal_candidate(candidate)
    if normalized_candidate is None:
        return None
    try:
        number = Decimal(normalized_candidate)
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


# Chuẩn hóa ISO 4217 alpha/numeric code về alpha-3 dựa trên reference data đóng gói.
def normalize_currency_code_value(value: Optional[str]) -> Optional[str]:
    """Normalize assigned ISO 4217 alpha-3 or numeric codes to alpha-3."""
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    candidate = re.sub(r"(?i)^ISO\s*4217\s*[:=-]?\s*", "", candidate).strip()

    import pycountry

    currency = None
    if re.fullmatch(r"[A-Za-z]{3}", candidate):
        currency = pycountry.currencies.get(alpha_3=candidate.upper())
    elif re.fullmatch(r"\d{3}", candidate):
        currency = pycountry.currencies.get(numeric=candidate)
    return str(currency.alpha_3) if currency is not None else None


def _phone_text_is_supported(candidate: str) -> bool:
    return re.fullmatch(r"[+0-9().\-\s]+", candidate) is not None


# Chuẩn hóa số điện thoại về hình thức quốc tế E.164 khi đã biết mã quốc gia mặc định.
def normalize_e164_value(value: Optional[str], default_country_code: Optional[str]) -> Optional[str]:
    """TRY_PARSE common phone formatting and emit conservative E.164-shaped text.

    ``default_country_code`` is used only for national numbers. The function does
    not perform carrier/subscriber allocation lookup and rejects extensions or
    alphabetic vanity-number interpretation.
    """
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    candidate = re.sub(r"(?i)^tel:\s*", "", candidate).strip()
    if ";" in candidate or not _phone_text_is_supported(candidate):
        return None
    digits = "".join(ch for ch in candidate if ch.isascii() and ch.isdigit())
    if not digits:
        return None

    if candidate.startswith("+"):
        international = digits
    elif digits.startswith("00"):
        international = digits[2:]
    elif default_country_code:
        code = normalize_null_token_value(default_country_code)
        if code is None:
            return None
        code = re.sub(r"\s+", "", code)
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
