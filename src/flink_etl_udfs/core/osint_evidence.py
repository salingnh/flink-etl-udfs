"""Pure OSINT evidence, provenance, confidence, and time transformations."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Optional

_VERIFICATION_STATUS_MAP = {
    "confirmed": "confirmed",
    "machine": "machine_correlated",
    "machine_correlated": "machine_correlated",
    "rejected": "rejected",
    "reviewed": "analyst_reviewed",
    "analyst_reviewed": "analyst_reviewed",
    "unverified": "unverified",
    "unknown": "unverified",
}


def content_sha256_value(value: Optional[str]) -> Optional[str]:
    """Return a deterministic SHA-256 digest for raw text evidence."""
    if value is None:
        return None
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def build_observation_id_value(
    source_url: Optional[str], entity_key: Optional[str], observed_at: Optional[str]
) -> Optional[str]:
    """Build a stable observation ID from source, entity key, and observation time."""
    if source_url is None or entity_key is None or observed_at is None:
        return None

    parts = [source_url.strip(), entity_key.strip(), observed_at.strip()]
    if any(not part for part in parts):
        return None

    payload = "\x1f".join(parts)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def normalize_confidence_value(value: Optional[str]) -> Optional[float]:
    """Parse a confidence score and accept only finite values in the inclusive 0..1 range."""
    if value is None:
        return None

    try:
        score = float(value.strip())
    except (AttributeError, ValueError):
        return None

    if score != score or score in {float("inf"), float("-inf")}:
        return None
    return score if 0.0 <= score <= 1.0 else None


def normalize_verification_status_value(value: Optional[str]) -> Optional[str]:
    """Map common OSINT verification labels into a compact controlled vocabulary."""
    if value is None:
        return None

    candidate = value.strip().lower().replace("-", "_").replace(" ", "_")
    if not candidate:
        return None
    return _VERIFICATION_STATUS_MAP.get(candidate)


def normalize_observed_at_utc_value(value: Optional[str]) -> Optional[str]:
    """Normalize an ISO-8601 timestamp with timezone into UTC Z form."""
    if value is None:
        return None

    candidate = value.strip()
    if not candidate:
        return None

    if candidate.endswith("Z"):
        candidate = f"{candidate[:-1]}+00:00"

    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError:
        return None

    if parsed.tzinfo is None:
        return None

    utc_value = parsed.astimezone(timezone.utc)
    return utc_value.isoformat().replace("+00:00", "Z")


__all__ = [
    "build_observation_id_value",
    "content_sha256_value",
    "normalize_confidence_value",
    "normalize_observed_at_utc_value",
    "normalize_verification_status_value",
]
