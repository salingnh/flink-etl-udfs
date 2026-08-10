"""Vietnam-specific deterministic normalization helpers."""

from __future__ import annotations

import re
from typing import Optional

from flink_etl_udfs.core.common import normalize_null_token_value

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

    The function validates structural format only. Registry validity and taxpayer
    status must be checked against an authoritative tax reference source.
    """
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    compact = re.sub(r"\s+", "", candidate)
    match = _VN_TAX_RE.fullmatch(compact)
    if not match:
        return None
    base, extension = match.groups()
    return base if extension is None else f"{base}-{extension}"


# Phân loại cấu trúc MST bằng nhãn trung tính, không suy diễn loại hình người nộp thuế.
def classify_vn_tax_id_structure_value(value: Optional[str]) -> Optional[str]:
    """Classify Vietnamese tax-ID structure as ``base_10`` or ``extended_13``."""
    normalized = normalize_vn_tax_id_value(value)
    if normalized is None:
        return None
    return "base_10" if "-" not in normalized else "extended_13"


__all__ = [
    "classify_vn_identity_id_value",
    "classify_vn_tax_id_structure_value",
    "normalize_vn_citizen_id_value",
    "normalize_vn_tax_id_value",
]
