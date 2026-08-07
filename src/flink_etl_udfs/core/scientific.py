"""Scalar helpers for genomics, climate and astronomy metadata."""

from __future__ import annotations

import re
from typing import Optional

from flink_etl_udfs.core.common import normalize_null_token_value

_IUPAC_DNA = set("ACGTRYSWKMBDHVN")


def normalize_chromosome_value(value: Optional[str]) -> Optional[str]:
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    candidate = re.sub(r"^(?i:chr)", "", candidate).upper()
    if candidate == "M":
        candidate = "MT"
    if candidate in {str(i) for i in range(1, 23)} | {"X", "Y", "MT"}:
        return candidate
    return candidate if re.fullmatch(r"[A-Z0-9_.-]{1,64}", candidate) else None


def normalize_dna_sequence_value(value: Optional[str]) -> Optional[str]:
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    sequence = re.sub(r"\s+", "", candidate).upper()
    if not sequence or any(base not in _IUPAC_DNA for base in sequence):
        return None
    return sequence


def normalize_vcf_genotype_value(value: Optional[str]) -> Optional[str]:
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    candidate = candidate.replace(" ", "")
    if re.fullmatch(r"(?:\.|\d+)(?:[|/](?:\.|\d+))+", candidate):
        return candidate
    return None


def normalize_cf_standard_name_value(value: Optional[str]) -> Optional[str]:
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    candidate = re.sub(r"[\s-]+", "_", candidate.casefold())
    return candidate if re.fullmatch(r"[a-z][a-z0-9_]*", candidate) else None


def normalize_grib_short_name_value(value: Optional[str]) -> Optional[str]:
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    candidate = candidate.strip().casefold()
    return candidate if re.fullmatch(r"[a-z0-9_]{1,32}", candidate) else None


def normalize_fits_keyword_value(value: Optional[str]) -> Optional[str]:
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    candidate = candidate.upper().replace(" ", "")
    return candidate if re.fullmatch(r"[A-Z0-9_-]{1,8}", candidate) else None


def normalize_celestial_frame_value(value: Optional[str]) -> Optional[str]:
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    key = re.sub(r"[^a-z0-9]", "", candidate.casefold())
    mapping = {
        "icrs": "ICRS",
        "fk5": "FK5",
        "fk4": "FK4",
        "galactic": "GALACTIC",
        "geocentrictrueecliptic": "GEOCENTRIC_TRUE_ECLIPTIC",
    }
    return mapping.get(key)


__all__ = [
    "normalize_celestial_frame_value",
    "normalize_cf_standard_name_value",
    "normalize_chromosome_value",
    "normalize_dna_sequence_value",
    "normalize_fits_keyword_value",
    "normalize_grib_short_name_value",
    "normalize_vcf_genotype_value",
]
