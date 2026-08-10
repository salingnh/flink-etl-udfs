"""Geospatial scalar normalization helpers."""

from __future__ import annotations

import re
from typing import Optional

from flink_etl_udfs.core.common import normalize_null_token_value


# Parse latitude và kiểm tra miền hợp lệ -90..90.
def normalize_latitude_value(value: Optional[str]) -> Optional[float]:
    """Parse latitude text as a floating-point value in the inclusive range -90..90."""
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    try:
        number = float(candidate)
    except ValueError:
        return None
    return number if -90.0 <= number <= 90.0 else None


# Parse longitude và kiểm tra miền hợp lệ -180..180.
def normalize_longitude_value(value: Optional[str]) -> Optional[float]:
    """Parse longitude text as a floating-point value in the inclusive range -180..180."""
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    try:
        number = float(candidate)
    except ValueError:
        return None
    return number if -180.0 <= number <= 180.0 else None


# Chuẩn hóa mã CRS dạng số về EPSG:<code>; không xác minh code có tồn tại trong EPSG registry.
def normalize_epsg_code_value(value: Optional[str]) -> Optional[str]:
    """Normalize a numeric CRS identifier to ``EPSG:<code>`` form."""
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    match = re.fullmatch(r"(?i)(?:EPSG\s*:\s*)?(\d{3,6})", candidate)
    if not match:
        return None
    code = int(match.group(1))
    return f"EPSG:{code}" if code > 0 else None


__all__ = ["normalize_epsg_code_value", "normalize_latitude_value", "normalize_longitude_value"]
