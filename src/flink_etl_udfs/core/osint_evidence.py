"""OSINT evidence and provenance transformations."""

from __future__ import annotations

import hashlib
from typing import Optional


# Tạo SHA-256 cho nội dung bằng chứng để kiểm tra tính toàn vẹn và deduplicate.
def content_sha256_value(value: Optional[str]) -> Optional[str]:
    """Return a deterministic SHA-256 digest for raw text evidence."""
    if value is None:
        return None
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


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


__all__ = ["build_observation_id_value", "content_sha256_value"]
