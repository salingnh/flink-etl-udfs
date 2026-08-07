"""Pure text normalization transformations."""

from __future__ import annotations

import re
import unicodedata
from typing import Optional

_WHITESPACE_RE = re.compile(r"\s+")


def trim_value(value: Optional[str]) -> Optional[str]:
    """Trim leading and trailing whitespace while preserving null values."""
    if value is None:
        return None
    return value.strip()


def normalize_whitespace_value(value: Optional[str]) -> Optional[str]:
    """Collapse all Unicode whitespace runs to one ASCII space and trim."""
    if value is None:
        return None
    return _WHITESPACE_RE.sub(" ", value).strip()


def normalize_unicode_nfc_value(value: Optional[str]) -> Optional[str]:
    """Normalize Unicode text to NFC without changing letter case."""
    if value is None:
        return None
    return unicodedata.normalize("NFC", value)


def null_if_blank_value(value: Optional[str]) -> Optional[str]:
    """Convert empty/whitespace-only strings to null; otherwise return trimmed text."""
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


__all__ = [
    "normalize_unicode_nfc_value",
    "normalize_whitespace_value",
    "null_if_blank_value",
    "trim_value",
]
