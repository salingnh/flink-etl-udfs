"""Vietnam-specific deterministic normalization helpers."""

from __future__ import annotations

import re
from typing import Optional

from flink_etl_udfs.core.common import (
    latin_name_search_key_value,
    normalize_account_identifier_value,
    normalize_address_text_value,
    normalize_e164_value,
    normalize_identifier_code_value,
    normalize_null_token_value,
    normalize_person_name_value,
)

_VN_CITIZEN_RE = re.compile(r"^(?:\d{9}|\d{12})$")
_VN_TAX_RE = re.compile(r"^(\d{10})(?:-?(\d{3}))?$")


# Chuẩn hóa CMND/CCCD Việt Nam theo cấu trúc 9 hoặc 12 chữ số, giữ số 0 ở đầu.
def normalize_vn_citizen_id_value(value: Optional[str]) -> Optional[str]:
    """Normalize Vietnamese CMND/CCCD shape while preserving leading zeroes."""
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    digits = "".join(ch for ch in candidate if ch.isascii() and ch.isdigit())
    return digits if _VN_CITIZEN_RE.fullmatch(digits) else None


# Phân loại định danh công dân theo độ dài; không khẳng định giấy tờ còn hiệu lực.
def classify_vn_identity_id_value(value: Optional[str]) -> Optional[str]:
    """Classify a normalized 9-digit CMND or 12-digit CCCD by length only."""
    normalized = normalize_vn_citizen_id_value(value)
    if normalized is None:
        return None
    return "cmnd_9" if len(normalized) == 9 else "cccd_12"


# Chuẩn hóa mã số thuế Việt Nam về dạng 10 số hoặc 10 số-3 số mở rộng.
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


# Phân loại cấu trúc MST bằng nhãn trung tính, không suy diễn loại hình người nộp thuế.
def classify_vn_tax_id_structure_value(value: Optional[str]) -> Optional[str]:
    """Classify Vietnamese tax-ID structure as ``base_10`` or ``extended_13``.

    The labels intentionally describe only the identifier shape. They do not infer
    taxpayer legal form, activity status, or registry validity.
    """
    normalized = normalize_vn_tax_id_value(value)
    if normalized is None:
        return None
    return "base_10" if "-" not in normalized else "extended_13"


# API legacy: giữ output cũ để không làm hỏng Flink SQL/job đã triển khai.
def classify_vn_tax_id_value(value: Optional[str]) -> Optional[str]:
    """Return the legacy ``enterprise``/``dependent_unit`` tax-ID classification.

    This function is retained for backward compatibility. New pipelines should use
    :func:`classify_vn_tax_id_structure_value`, whose labels describe only shape and
    avoid over-interpreting a 10-digit tax identifier as an enterprise.
    """
    normalized = normalize_vn_tax_id_value(value)
    if normalized is None:
        return None
    return "enterprise" if "-" not in normalized else "dependent_unit"


# Profile Việt Nam của bộ chuẩn hóa số điện thoại E.164, dùng mã quốc gia +84.
def normalize_vn_phone_value(value: Optional[str]) -> Optional[str]:
    """Normalize a Vietnamese phone-number shape to E.164 using country code +84."""
    return normalize_e164_value(value, "+84")


# Alias tương thích ngược cho chuẩn hóa tên người generic Unicode NFC + whitespace.
def normalize_vn_name_value(value: Optional[str]) -> Optional[str]:
    """Normalize a Vietnamese personal name via the generic person-name transform."""
    return normalize_person_name_value(value)


# Alias Việt Nam cho khóa tìm kiếm tên Latin không dấu; chỉ dùng blocking/candidate generation.
def vietnamese_name_search_key_value(value: Optional[str]) -> Optional[str]:
    """Build an accent-insensitive blocking/search key for Vietnamese names."""
    return latin_name_search_key_value(value)


# Alias tương thích cho chuẩn hóa địa chỉ text; không tự suy đoán tỉnh/huyện/xã.
def normalize_vn_address_value(value: Optional[str]) -> Optional[str]:
    """Normalize Vietnamese free-text addresses without guessing administrative codes."""
    return normalize_address_text_value(value)


# Alias domain cho mã trường; logic chuẩn hóa thực tế dùng generic identifier-code helper.
def normalize_school_code_value(value: Optional[str]) -> Optional[str]:
    """Normalize a school code via the generic business-identifier transform."""
    return normalize_identifier_code_value(value)


# Alias domain cho mã giáo viên; logic chuẩn hóa không phụ thuộc một dataset giáo dục cụ thể.
def normalize_teacher_code_value(value: Optional[str]) -> Optional[str]:
    """Normalize a teacher code via the generic business-identifier transform."""
    return normalize_identifier_code_value(value)


# Alias domain cho mã học sinh; giữ API cũ nhưng dùng generic identifier-code helper.
def normalize_student_code_value(value: Optional[str]) -> Optional[str]:
    """Normalize a student code via the generic business-identifier transform."""
    return normalize_identifier_code_value(value)


# Chuẩn hóa năm học hai năm liên tiếp, ví dụ 2025/26 thành 2025-2026.
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


# Chuẩn hóa nhãn người gửi SMS ở mức text; không thay thế validator theo nhà mạng/quốc gia.
def normalize_sms_brandname_value(value: Optional[str]) -> Optional[str]:
    """Normalize an SMS sender brand name by removing whitespace and uppercasing."""
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    compact = re.sub(r"\s+", "", candidate).upper()
    return compact or None


# Alias tương thích cho mã tài khoản dạng chữ-số; không thay thế IBAN hoặc rule của từng ngân hàng.
def normalize_bank_account_value(value: Optional[str]) -> Optional[str]:
    """Normalize a bank-account identifier via the generic account/reference helper."""
    return normalize_account_identifier_value(value)


# Tạo blocking key phục vụ entity resolution trong profile Việt Nam từ tên, điện thoại và email.
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
    "classify_vn_tax_id_structure_value",
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
