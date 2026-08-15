"""Deterministic helpers for STIX/CTI and security interchange identifiers."""

from __future__ import annotations

import re
import uuid
from typing import Optional

from flink_etl_udfs.core.common import normalize_null_token_value


def normalize_stix_type_value(value: Optional[str]) -> Optional[str]:
    """Normalize common STIX type separators to lowercase hyphenated form."""
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    candidate = re.sub(r"[\s_]+", "-", candidate.casefold())
    candidate = re.sub(r"-+", "-", candidate).strip("-")
    return candidate if re.fullmatch(r"[a-z][a-z0-9-]*", candidate) else None


def normalize_stix_id_value(value: Optional[str]) -> Optional[str]:
    """TRY_PARSE a STIX identifier and canonicalize both type and UUID text."""
    candidate = normalize_null_token_value(value)
    if candidate is None or "--" not in candidate:
        return None
    stix_type_text, object_id_text = candidate.split("--", 1)
    stix_type = normalize_stix_type_value(stix_type_text)
    if stix_type is None:
        return None
    object_id_text = object_id_text.strip().strip("{}")
    try:
        object_id = str(uuid.UUID(object_id_text))
    except ValueError:
        return None
    return f"{stix_type}--{object_id}"


def normalize_attack_technique_id_value(value: Optional[str]) -> Optional[str]:
    """TRY_PARSE ATT&CK technique/sub-technique aliases to canonical ID text."""
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    candidate = re.sub(r"(?i)^(?:MITRE\s+)?ATT&CK\s*[:#-]?\s*", "", candidate)
    candidate = re.sub(r"(?i)^TECHNIQUE\s*[:#-]?\s*", "", candidate)
    candidate = candidate.upper().replace(" ", "")
    candidate = re.sub(r"[_/-]", ".", candidate)
    candidate = re.sub(r"\.+", ".", candidate)
    return candidate if re.fullmatch(r"T\d{4}(?:\.\d{3})?", candidate) else None


__all__ = [
    "normalize_attack_technique_id_value",
    "normalize_stix_id_value",
    "normalize_stix_type_value",
]
