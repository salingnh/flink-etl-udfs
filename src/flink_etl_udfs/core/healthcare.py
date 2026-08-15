"""Healthcare interchange identifier normalizers for FHIR, HL7 v2 and DICOM."""

from __future__ import annotations

import re
import uuid
from typing import Optional

from flink_etl_udfs.core.common import normalize_null_token_value

_FHIR_ID_RE = re.compile(r"^[A-Za-z0-9\-.]{1,64}$")
_DICOM_UID_RE = re.compile(r"^(?:0|[1-9]\d*)(?:\.(?:0|[1-9]\d*))*$")


# Kiểm tra FHIR resource id theo character/length constraints của FHIR.
def normalize_fhir_id_value(value: Optional[str]) -> Optional[str]:
    """Normalize a bare FHIR id or contained-reference ``#id`` to the id token."""
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    if candidate.startswith("#"):
        candidate = candidate[1:].strip()
    return candidate if _FHIR_ID_RE.fullmatch(candidate) else None


# Chuẩn hóa local/relative FHIR reference như Patient/123 hoặc #contained-id.
def normalize_fhir_reference_value(value: Optional[str]) -> Optional[str]:
    """TRY_PARSE common local/relative FHIR references and UUID URNs."""
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None

    lowered = candidate.casefold()
    if lowered.startswith("urn:uuid:"):
        try:
            return "urn:uuid:" + str(uuid.UUID(candidate[9:].strip().strip("{}")))
        except ValueError:
            return None

    if candidate.startswith("#"):
        local_id = normalize_fhir_id_value(candidate)
        return f"#{local_id}" if local_id else None

    match = re.fullmatch(r"\s*([A-Z][A-Za-z0-9]+)\s*/\s*([^/\s]+)\s*", candidate)
    if not match:
        return None
    resource_type, resource_id = match.groups()
    normalized_id = normalize_fhir_id_value(resource_id)
    return f"{resource_type}/{normalized_id}" if normalized_id else None


# Chuẩn hóa HL7 v2 message type như ADT^A01.
def normalize_hl7_message_type_value(value: Optional[str]) -> Optional[str]:
    """TRY_PARSE common HL7 v2 message-type separators to ``TYPE^TRIGGER`` form."""
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    candidate = candidate.upper().strip()
    parts = [part for part in re.split(r"[\s~^_/-]+", candidate) if part]
    if len(parts) not in {2, 3}:
        return None
    if not re.fullmatch(r"[A-Z0-9]{3}", parts[0]) or not re.fullmatch(r"[A-Z0-9]{3}", parts[1]):
        return None
    if len(parts) == 3 and re.fullmatch(r"[A-Z0-9_]+", parts[2]) is None:
        return None
    return "^".join(parts)


# Kiểm tra DICOM UID/OID syntax và giới hạn 64 ký tự.
def normalize_dicom_uid_value(value: Optional[str]) -> Optional[str]:
    """TRY_PARSE DICOM UID/OID labels and emit canonical numeric dot notation."""
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    candidate = re.sub(r"(?i)^(?:urn:oid:|OID\s*[:#]?\s*)", "", candidate)
    candidate = re.sub(r"\s*\.\s*", ".", candidate.strip())
    if len(candidate) > 64:
        return None
    return candidate if _DICOM_UID_RE.fullmatch(candidate) else None


__all__ = [
    "normalize_dicom_uid_value",
    "normalize_fhir_id_value",
    "normalize_fhir_reference_value",
    "normalize_hl7_message_type_value",
]
