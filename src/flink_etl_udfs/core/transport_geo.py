"""Geospatial scalar normalization helpers."""

from __future__ import annotations

import re
from typing import Optional
from urllib.parse import urlsplit

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
    """TRY_PARSE common EPSG code/URN/URL representations to ``EPSG:<code>``."""
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None

    patterns = (
        r"(?i)(?:EPSG\s*[:# ]\s*)?(\d{3,6})",
        r"(?i)urn:ogc:def:crs:EPSG(?::[^:]*)?::?(\d{3,6})",
    )
    code_text = None
    for pattern in patterns:
        match = re.fullmatch(pattern, candidate)
        if match:
            code_text = match.group(1)
            break

    if code_text is None and "://" in candidate:
        try:
            parts = urlsplit(candidate)
            path = parts.path.rstrip("/")
            match = re.search(r"(?i)/crs/EPSG/(?:\d+|0)/(\d{3,6})$", path)
            if match:
                code_text = match.group(1)
        except ValueError:
            return None

    if code_text is None:
        return None
    code = int(code_text)
    return f"EPSG:{code}" if code > 0 else None


__all__ = ["normalize_epsg_code_value", "normalize_latitude_value", "normalize_longitude_value"]
