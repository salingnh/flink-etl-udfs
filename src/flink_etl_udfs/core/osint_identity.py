"""OSINT account-handle normalization helpers."""

from __future__ import annotations

import unicodedata
from typing import Optional


# Chuẩn hóa username/handle công khai mà không thay đổi quy tắc hoa-thường của từng nền tảng.
def normalize_username_value(value: Optional[str]) -> Optional[str]:
    """Normalize a public account handle without changing provider-specific case semantics."""
    if value is None:
        return None

    candidate = unicodedata.normalize("NFC", value.strip())
    candidate = candidate.lstrip("@").strip()
    return candidate or None


__all__ = ["normalize_username_value"]
