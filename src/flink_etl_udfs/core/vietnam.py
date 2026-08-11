"""Vietnam-specific deterministic normalization helpers."""

from __future__ import annotations

import re
from typing import Optional

from flink_etl_udfs.core.common import normalize_null_token_value

_VN_CITIZEN_RE = re.compile(r"^(?:\d{9}|\d{12})$")
_VN_TAX_RE = re.compile(r"^(\d{10})(?:-?(\d{3}))?$")
_VN_MOBILE_RE = re.compile(r"^0[35789]\d{8}$")

# Mapping đợt chuyển đổi mã mạng di động Việt Nam 11 số -> 10 số năm 2018.
_VN_LEGACY_MOBILE_PREFIXES = {
    # Viettel
    "0162": "032",
    "0163": "033",
    "0164": "034",
    "0165": "035",
    "0166": "036",
    "0167": "037",
    "0168": "038",
    "0169": "039",
    # VinaPhone
    "0123": "083",
    "0124": "084",
    "0125": "085",
    "0127": "081",
    "0129": "082",
    # MobiFone
    "0120": "070",
    "0121": "079",
    "0122": "077",
    "0126": "076",
    "0128": "078",
    # Vietnamobile
    "0186": "056",
    "0188": "058",
    # Gmobile / Gtel
    "0199": "059",
}


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


# Chuẩn hóa số di động Việt Nam, gồm cả mapping đầu số 11 số cũ sang 10 số hiện hành.
def normalize_vn_mobile_phone_value(value: Optional[str]) -> Optional[str]:
    """Normalize a Vietnamese mobile number to national 10-digit ``0xxxxxxxxx`` form.

    Accepted input can use national ``0...`` form or international ``84``/``+84``/``0084``
    form. Historical 11-digit mobile prefixes are converted using the official 2018
    network-code migration map. The function performs structural normalization only;
    it does not verify subscriber allocation, carrier ownership after mobile-number
    portability, or whether the number is currently active.
    """
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None

    digits = "".join(ch for ch in candidate if ch.isascii() and ch.isdigit())
    if not digits:
        return None

    if digits.startswith("0084"):
        national = "0" + digits[4:]
    elif digits.startswith("84") and len(digits) in {11, 12}:
        national = "0" + digits[2:]
    elif digits.startswith("0"):
        national = digits
    else:
        return None

    if len(national) == 11:
        replacement = next(
            (
                new_prefix + national[len(old_prefix) :]
                for old_prefix, new_prefix in _VN_LEGACY_MOBILE_PREFIXES.items()
                if national.startswith(old_prefix)
            ),
            None,
        )
        if replacement is None:
            return None
        national = replacement

    return national if _VN_MOBILE_RE.fullmatch(national) else None


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
    "normalize_vn_mobile_phone_value",
    "normalize_vn_tax_id_value",
]
