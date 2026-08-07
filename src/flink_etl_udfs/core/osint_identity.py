"""Pure OSINT identity and account normalization transformations."""

from __future__ import annotations

import re
import unicodedata
from typing import Optional

_WHITESPACE_RE = re.compile(r"\s+")
_NON_WORD_RE = re.compile(r"[^\w]+", flags=re.UNICODE)


def normalize_username_value(value: Optional[str]) -> Optional[str]:
    """Normalize a public account handle without changing provider-specific case semantics."""
    if value is None:
        return None

    candidate = unicodedata.normalize("NFC", value.strip())
    candidate = candidate.lstrip("@").strip()
    return candidate or None


def normalize_platform_value(value: Optional[str]) -> Optional[str]:
    """Normalize a platform/domain label to a compact lowercase representation."""
    if value is None:
        return None

    candidate = unicodedata.normalize("NFC", value.strip()).lower()
    candidate = candidate.removeprefix("www.").rstrip(".")
    return candidate or None


def normalize_name_search_key_value(value: Optional[str]) -> Optional[str]:
    """Build an accent-insensitive search key for candidate generation, not canonical identity."""
    if value is None:
        return None

    normalized = unicodedata.normalize("NFKD", value.strip()).casefold()
    without_marks = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    collapsed_punctuation = _NON_WORD_RE.sub(" ", without_marks)
    search_key = _WHITESPACE_RE.sub(" ", collapsed_punctuation).strip()
    return search_key or None


def classify_account_identifier_value(value: Optional[str]) -> Optional[str]:
    """Classify a public account identifier using conservative syntax heuristics."""
    if value is None:
        return None

    candidate = value.strip()
    if not candidate:
        return None

    if candidate.count("@") == 1:
        local, domain = candidate.rsplit("@", 1)
        if local and "." in domain and not domain.startswith(".") and not domain.endswith("."):
            return "email"

    digits = "".join(ch for ch in candidate if ch.isdigit())
    non_phone_chars = [ch for ch in candidate if not (ch.isdigit() or ch in "+-(). /\t")]
    if 7 <= len(digits) <= 15 and not non_phone_chars:
        return "phone"

    return "username"


__all__ = [
    "classify_account_identifier_value",
    "normalize_name_search_key_value",
    "normalize_platform_value",
    "normalize_username_value",
]
