"""Healthcare interchange identifier normalizers for FHIR, HL7 v2 and DICOM."""

from __future__ import annotations

import re
from typing import Optional

from flink_etl_udfs.core.common import normalize_null_token_value

_FHIR_ID_RE = re.compile(r"^[A-Za-z0-9\-.]{1,64}$")
_DICOM_UID_RE = re.compile(r"^(?:0|[1-9]\d*)(?:\.(?:0|[1-9]\d*))*$")


def normalize_fhir_id_value(value: Optional[str]) -> Optional[str]:
    candidate = normalize_null_token_value(value)
    return candidate if candidate and _FHIR_ID_RE.fullmatch(candidate) else None


def normalize_fhir_reference_value(value: Optional[str]) -> Optional[str]:
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    if candidate.startswith("#"):
        local_id = normalize_fhir_id_value(candidate[1:])
        return f"#{local_id}" if local_id else None
    if "/" not in candidate:
        return None
    resource_type, resource_id = candidate.split("/", 1)
    if not re.fullmatch(r"[A-Z][A-Za-z0-9]+", resource_type):
        return None
    normalized_id = normalize_fhir_id_value(resource_id)
    return f"{resource_type}/{normalized_id}" if normalized_id else None


def normalize_hl7_message_type_value(value: Optional[str]) -> Optional[str]:
    """Normalize common HL7 v2 message type strings such as ``ADT^A01``."""
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    candidate = candidate.upper().replace("~", "^")
    candidate = re.sub(r"\s+", "", candidate)
    return candidate if re.fullmatch(r"[A-Z0-9]{3}\^[A-Z0-9]{3}(?:\^[A-Z0-9_]+)?", candidate) else None


def normalize_dicom_uid_value(value: Optional[str]) -> Optional[str]:
    candidate = normalize_null_token_value(value)
    if candidate is None or len(candidate) > 64:
        return None
    return candidate if _DICOM_UID_RE.fullmatch(candidate) else None


def normalize_dicom_modality_value(value: Optional[str]) -> Optional[str]:
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    candidate = candidate.upper()
    return candidate if re.fullmatch(r"[A-Z0-9]{1,16}", candidate) else None


__all__ = [
    "normalize_dicom_modality_value",
    "normalize_dicom_uid_value",
    "normalize_fhir_id_value",
    "normalize_fhir_reference_value",
    "normalize_hl7_message_type_value",
]
