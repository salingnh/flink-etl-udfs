"""Pure masking and deterministic fingerprinting transformations."""

from __future__ import annotations

import hashlib
from typing import Optional


def sha256_fingerprint_value(value: Optional[str]) -> Optional[str]:
    """Return a deterministic SHA-256 fingerprint while preserving null values."""
    if value is None:
        return None

    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def mask_text_value(value: Optional[str]) -> Optional[str]:
    """Mask the middle of a string while retaining its boundary characters."""
    if value is None:
        return None

    if len(value) <= 2:
        return "*" * len(value)

    return value[0] + ("*" * (len(value) - 2)) + value[-1]


def mask_email_value(value: Optional[str]) -> Optional[str]:
    """Mask the local part of a syntactically simple email address.

    This is intentionally not an email validator. Invalid/unexpected inputs are
    masked as generic text instead of being silently rejected.
    """
    if value is None:
        return None

    local, separator, domain = value.partition("@")
    if not separator or not local or not domain:
        return mask_text_value(value)

    return f"{mask_text_value(local)}@{domain}"


__all__ = [
    "mask_email_value",
    "mask_text_value",
    "sha256_fingerprint_value",
]
