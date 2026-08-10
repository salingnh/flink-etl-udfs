"""Standards-based OSINT compliance identifier transformations."""

from __future__ import annotations

from typing import Optional


# Chuẩn hóa và kiểm tra LEI theo ISO 17442 mod-97.
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


__all__ = ["normalize_lei_value"]
