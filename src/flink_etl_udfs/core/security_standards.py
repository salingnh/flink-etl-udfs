"""Deterministic helpers for STIX/CTI and security interchange identifiers."""

from __future__ import annotations

import re
import uuid
from typing import Optional

from flink_etl_udfs.core.common import normalize_null_token_value

_STIX_ID_RE = re.compile(r"^([a-z][a-z0-9-]*)--([0-9a-fA-F-]{36})$")


def normalize_stix_type_value(value: Optional[str]) -> Optional[str]:
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    candidate = candidate.casefold().replace("_", "-")
    return candidate if re.fullmatch(r"[a-z][a-z0-9-]*", candidate) else None


def normalize_stix_id_value(value: Optional[str]) -> Optional[str]:
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    match = _STIX_ID_RE.fullmatch(candidate)
    if not match:
        return None
    stix_type = normalize_stix_type_value(match.group(1))
    try:
        object_id = str(uuid.UUID(match.group(2)))
    except ValueError:
        return None
    return f"{stix_type}--{object_id}" if stix_type else None


def normalize_attack_technique_id_value(value: Optional[str]) -> Optional[str]:
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    candidate = candidate.upper().replace(" ", "")
    candidate = candidate.replace("_", ".")
    return candidate if re.fullmatch(r"T\d{4}(?:\.\d{3})?", candidate) else None


__all__ = [
    "normalize_attack_technique_id_value",
    "normalize_stix_id_value",
    "normalize_stix_type_value",
]
