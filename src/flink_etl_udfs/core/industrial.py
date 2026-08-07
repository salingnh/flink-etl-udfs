"""Industrial/IoT identifier helpers for OPC UA and DLMS/COSEM."""

from __future__ import annotations

import re
from typing import Optional

from flink_etl_udfs.core.common import normalize_null_token_value

_OPCUA_NODE_RE = re.compile(r"^(?:ns=(\d+);)?([isgb])=(.+)$", re.IGNORECASE)


def normalize_opcua_node_id_value(value: Optional[str]) -> Optional[str]:
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    match = _OPCUA_NODE_RE.fullmatch(candidate)
    if not match:
        return None
    namespace, identifier_type, identifier = match.groups()
    if not identifier:
        return None
    ns = int(namespace or "0")
    if not 0 <= ns <= 65535:
        return None
    kind = identifier_type.lower()
    if kind == "i" and not identifier.isdigit():
        return None
    prefix = "" if ns == 0 else f"ns={ns};"
    return f"{prefix}{kind}={identifier}"


def normalize_obis_code_value(value: Optional[str]) -> Optional[str]:
    """Normalize the common textual OBIS form ``A-B:C.D.E*F``.

    OBIS profiles differ by medium/device, so this validates syntax rather than
    attempting semantic catalogue validation.
    """
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    candidate = re.sub(r"\s+", "", candidate)
    match = re.fullmatch(
        r"(?:(\d{1,3})-)?(\d{1,3}):(\d{1,3})\.(\d{1,3})\.(\d{1,3})(?:\*(\d{1,3}))?",
        candidate,
    )
    if not match:
        return None
    groups = [int(x) if x is not None else None for x in match.groups()]
    if any(x is not None and not 0 <= x <= 255 for x in groups):
        return None
    a, b, c, d, e, f = groups
    prefix = f"{a}-" if a is not None else ""
    suffix = f"*{f}" if f is not None else ""
    return f"{prefix}{b}:{c}.{d}.{e}{suffix}"


def normalize_telemetry_quality_value(value: Optional[str]) -> Optional[str]:
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    key = candidate.casefold().replace("_", " ").strip()
    mapping = {
        "good": "good",
        "ok": "good",
        "uncertain": "uncertain",
        "bad": "bad",
        "invalid": "bad",
        "offline": "offline",
    }
    return mapping.get(key)


__all__ = [
    "normalize_obis_code_value",
    "normalize_opcua_node_id_value",
    "normalize_telemetry_quality_value",
]
