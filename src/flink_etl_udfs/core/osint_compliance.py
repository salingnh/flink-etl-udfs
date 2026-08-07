"""Pure OSINT company-registry, watchlist, and ownership transformations."""

from __future__ import annotations

from typing import Optional

_ENTITY_TYPE_MAP = {
    "account": "online_account",
    "company": "organization",
    "domain": "domain",
    "document": "document",
    "individual": "person",
    "ip": "ip_address",
    "ip_address": "ip_address",
    "online_account": "online_account",
    "org": "organization",
    "organisation": "organization",
    "organization": "organization",
    "person": "person",
    "repository": "code_repository",
    "code_repository": "code_repository",
}


def normalize_lei_value(value: Optional[str]) -> Optional[str]:
    """Normalize and validate a Legal Entity Identifier using ISO 17442 mod-97 rules."""
    if value is None:
        return None

    candidate = "".join(ch for ch in value.strip().upper() if not ch.isspace())
    if len(candidate) != 20 or not candidate.isalnum():
        return None

    numeric = "".join(str(ord(ch) - 55) if ch.isalpha() else ch for ch in candidate)
    try:
        valid = int(numeric) % 97 == 1
    except ValueError:
        return None
    return candidate if valid else None


def normalize_ownership_percentage_value(value: Optional[str]) -> Optional[float]:
    """Parse an ownership percentage in the inclusive 0..100 range."""
    if value is None:
        return None

    candidate = value.strip().removesuffix("%").strip()
    if not candidate:
        return None

    try:
        percentage = float(candidate)
    except ValueError:
        return None

    if percentage != percentage or percentage in {float("inf"), float("-inf")}:
        return None
    return percentage if 0.0 <= percentage <= 100.0 else None


def normalize_entity_type_value(value: Optional[str]) -> Optional[str]:
    """Normalize common OSINT graph entity labels into a controlled vocabulary."""
    if value is None:
        return None

    candidate = value.strip().lower().replace("-", "_").replace(" ", "_")
    if not candidate:
        return None
    return _ENTITY_TYPE_MAP.get(candidate)


__all__ = [
    "normalize_entity_type_value",
    "normalize_lei_value",
    "normalize_ownership_percentage_value",
]
