"""Self-contained PyFlink UDFs for Vietnam-specific deterministic transforms."""

from __future__ import annotations

import re
from typing import Optional

from flink_etl_udfs.udfs._safe import try_udf

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
_VN_CITIZEN_RE = re.compile(r"^(?:\d{9}|\d{12})$")
_VN_TAX_RE = re.compile(r"^(\d{10})(?:-?(\d{3}))?$")
_VN_MOBILE_RE = re.compile(r"^0[35789]\d{8}$")

# Closed historical migration map from Vietnam's 2018 mobile-number conversion.
_VN_LEGACY_MOBILE_PREFIXES = {
    "0162": "032",
    "0163": "033",
    "0164": "034",
    "0165": "035",
    "0166": "036",
    "0167": "037",
    "0168": "038",
    "0169": "039",
    "0123": "083",
    "0124": "084",
    "0125": "085",
    "0127": "081",
    "0129": "082",
    "0120": "070",
    "0121": "079",
    "0122": "077",
    "0126": "076",
    "0128": "078",
    "0186": "056",
    "0188": "058",
    "0199": "059",
}


def _clean(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    candidate = value.strip()
    return None if candidate.casefold() in _NULL_TOKENS else candidate


def _strip_known_prefix(value: str, prefixes: str) -> str:
    return re.sub(rf"(?i)^(?:{prefixes})\s*[:#-]?\s*", "", value).strip()


def _normalize_vn_citizen_id(value: Optional[str]) -> Optional[str]:
    candidate = _clean(value)
    if candidate is None:
        return None
    candidate = _strip_known_prefix(candidate, r"CMND|CCCD|CĂN\s*CƯỚC|CAN\s*CUOC")
    if re.fullmatch(r"[0-9.\-\s]+", candidate) is None:
        return None
    digits = re.sub(r"[.\-\s]+", "", candidate)
    return digits if _VN_CITIZEN_RE.fullmatch(digits) else None


def _classify_vn_identity_id(value: Optional[str]) -> Optional[str]:
    normalized = _normalize_vn_citizen_id(value)
    if normalized is None:
        return None
    return "cmnd_9" if len(normalized) == 9 else "cccd_12"


def _normalize_vn_mobile_phone(value: Optional[str]) -> Optional[str]:
    candidate = _clean(value)
    if candidate is None:
        return None
    candidate = re.sub(r"(?i)^tel:\s*", "", candidate).strip()
    if re.fullmatch(r"[+0-9().\-\s]+", candidate) is None:
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


def _normalize_vn_tax_id(value: Optional[str]) -> Optional[str]:
    candidate = _clean(value)
    if candidate is None:
        return None
    candidate = _strip_known_prefix(candidate, r"MST|MÃ\s*SỐ\s*THUẾ|MA\s*SO\s*THUE|TAX\s*ID")
    if re.fullmatch(r"[0-9.\-\s]+", candidate) is None:
        return None
    compact = re.sub(r"[.\s]+", "", candidate)
    match = _VN_TAX_RE.fullmatch(compact)
    if not match:
        return None
    base, extension = match.groups()
    return base if extension is None else f"{base}-{extension}"


def _classify_vn_tax_id_structure(value: Optional[str]) -> Optional[str]:
    normalized = _normalize_vn_tax_id(value)
    if normalized is None:
        return None
    return "extended_13" if "-" in normalized else "base_10"


def _string_udf(function):
    return try_udf(
        function,
        cast_types=["STRING"],
        result_type="STRING",
        deterministic=True,
    )


normalize_vn_citizen_id = _string_udf(_normalize_vn_citizen_id)
classify_vn_identity_id = _string_udf(_classify_vn_identity_id)
normalize_vn_mobile_phone = _string_udf(_normalize_vn_mobile_phone)
normalize_vn_tax_id = _string_udf(_normalize_vn_tax_id)
classify_vn_tax_id_structure = _string_udf(_classify_vn_tax_id_structure)


__all__ = [
    "classify_vn_identity_id",
    "classify_vn_tax_id_structure",
    "normalize_vn_citizen_id",
    "normalize_vn_mobile_phone",
    "normalize_vn_tax_id",
]
