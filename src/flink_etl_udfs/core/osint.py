"""OSINT-specific account and observation transformations."""

from __future__ import annotations

import hashlib
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


# Tạo observation ID ổn định từ nguồn, khóa thực thể và thời điểm quan sát.
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


__all__ = ["build_observation_id_value", "normalize_username_value"]
