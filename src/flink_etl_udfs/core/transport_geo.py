"""Transport and geospatial scalar normalization helpers."""

from __future__ import annotations

import re
from typing import Optional

from flink_etl_udfs.core.common import normalize_null_token_value


def normalize_gtfs_id_value(value: Optional[str]) -> Optional[str]:
    """Normalize a GTFS identifier by trimming/collapsing whitespace while rejecting embedded line breaks."""
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    candidate = re.sub(r"\s+", " ", candidate).strip()
    return candidate if candidate and "\n" not in candidate and "\r" not in candidate else None


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


__all__ = [
    "normalize_epsg_code_value",
    "normalize_gtfs_id_value",
    "normalize_latitude_value",
    "normalize_longitude_value",
]
