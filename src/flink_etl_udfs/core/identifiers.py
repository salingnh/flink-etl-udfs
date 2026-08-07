"""Pure identifier normalization transformations."""

from __future__ import annotations

from typing import Optional


def normalize_email_value(value: Optional[str]) -> Optional[str]:
    """Trim an email and lowercase only its domain component.

    The local part is intentionally preserved because its case semantics can be
    provider-specific. This function normalizes; it does not claim validation.
    """
    if value is None:
        return None

    candidate = value.strip()
    if not candidate:
        return None

    local, separator, domain = candidate.rpartition("@")
    if not separator or not local or not domain:
        return None

    return f"{local}@{domain.lower()}"


def digits_only_value(value: Optional[str]) -> Optional[str]:
    """Keep ASCII digits only; return null when no digits remain."""
    if value is None:
        return None

    digits = "".join(ch for ch in value if "0" <= ch <= "9")
    return digits or None


__all__ = ["digits_only_value", "normalize_email_value"]
