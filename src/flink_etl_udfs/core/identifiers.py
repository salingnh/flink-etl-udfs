"""Pure identifier normalization transformations."""

from __future__ import annotations

import re
from typing import Optional


def normalize_email_value(value: Optional[str]) -> Optional[str]:
    """Normalize common email representations while preserving local-part case.

    Supported source forms include a bare address, ``mailto:`` URI, and a single
    display-name angle-bracket form. The domain is IDNA-normalized/lowercased. This
    is conservative structural normalization, not full RFC mailbox validation.
    """
    if value is None:
        return None

    candidate = value.strip()
    if not candidate:
        return None

    if candidate.casefold().startswith("mailto:"):
        candidate = candidate[7:].split("?", 1)[0].strip()

    angle = re.fullmatch(r"[^<>]*<\s*([^<>]+?)\s*>", candidate)
    if angle:
        candidate = angle.group(1).strip()

    if any(ch.isspace() for ch in candidate) or candidate.count("@") != 1:
        return None
    local, domain = candidate.split("@", 1)
    if not local or not domain:
        return None

    try:
        normalized_domain = domain.rstrip(".").encode("idna").decode("ascii").lower()
    except UnicodeError:
        return None
    if not normalized_domain or "." not in normalized_domain:
        return None
    return f"{local}@{normalized_domain}"


def digits_only_value(value: Optional[str]) -> Optional[str]:
    """Keep ASCII digits only; return null when no digits remain."""
    if value is None:
        return None

    digits = "".join(ch for ch in value if "0" <= ch <= "9")
    return digits or None


__all__ = ["digits_only_value", "normalize_email_value"]
