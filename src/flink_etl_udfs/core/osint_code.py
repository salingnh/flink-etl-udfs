"""Pure OSINT source-code and repository identifier transformations."""

from __future__ import annotations

import re
from typing import Optional
from urllib.parse import urlsplit, urlunsplit

from flink_etl_udfs.core.osint_web import canonicalize_url_value

_GIT_OBJECT_RE = re.compile(r"^[0-9a-fA-F]+$")


def normalize_repository_url_value(value: Optional[str]) -> Optional[str]:
    """Normalize an HTTP(S) repository URL and remove a trailing .git suffix."""
    canonical = canonicalize_url_value(value)
    if canonical is None:
        return None

    parts = urlsplit(canonical)
    path = parts.path.rstrip("/")
    if path.endswith(".git"):
        path = path[:-4]
    if not path:
        path = "/"
    return urlunsplit((parts.scheme, parts.netloc, path, "", ""))


def normalize_git_object_id_value(value: Optional[str]) -> Optional[str]:
    """Normalize a full Git SHA-1 or SHA-256 object identifier."""
    if value is None:
        return None

    candidate = value.strip().lower()
    if len(candidate) not in {40, 64} or not _GIT_OBJECT_RE.fullmatch(candidate):
        return None
    return candidate


def classify_git_object_hash_value(value: Optional[str]) -> Optional[str]:
    """Classify a full Git object identifier as SHA-1 or SHA-256."""
    normalized = normalize_git_object_id_value(value)
    if normalized is None:
        return None
    return "sha1" if len(normalized) == 40 else "sha256"


__all__ = [
    "classify_git_object_hash_value",
    "normalize_git_object_id_value",
    "normalize_repository_url_value",
]
