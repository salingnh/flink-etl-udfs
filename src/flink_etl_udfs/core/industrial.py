"""Industrial/IoT identifier helpers for OPC UA and DLMS/COSEM."""

from __future__ import annotations

import base64
import re
import uuid
from typing import Optional

from flink_etl_udfs.core.common import normalize_null_token_value

_OPCUA_NODE_RE = re.compile(r"^(?:ns\s*=\s*(\d+)\s*;\s*)?([isgb])\s*=\s*(.+)$", re.IGNORECASE)


# Chuẩn hóa OPC UA NodeId về representation ổn định cho namespace và identifier type.
def normalize_opcua_node_id_value(value: Optional[str]) -> Optional[str]:
    """TRY_PARSE common OPC UA NodeId spacing/prefix forms and canonicalize values."""
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    candidate = re.sub(r"(?i)^NodeId\s*[:#-]?\s*", "", candidate)
    match = _OPCUA_NODE_RE.fullmatch(candidate)
    if not match:
        return None
    namespace, identifier_type, identifier = match.groups()
    identifier = identifier.strip()
    if not identifier:
        return None
    ns = int(namespace or "0")
    if not 0 <= ns <= 65535:
        return None
    kind = identifier_type.lower()

    if kind == "i":
        if not identifier.isdigit():
            return None
        identifier = str(int(identifier))
    elif kind == "g":
        try:
            identifier = str(uuid.UUID(identifier.strip("{}")))
        except ValueError:
            return None
    elif kind == "b":
        try:
            raw = base64.b64decode(identifier, validate=True)
        except (ValueError, TypeError):
            return None
        identifier = base64.b64encode(raw).decode("ascii")

    prefix = "" if ns == 0 else f"ns={ns};"
    return f"{prefix}{kind}={identifier}"


# Chuẩn hóa textual OBIS A-B:C.D.E*F; semantic catalogue validation nằm ở reference layer.
def normalize_obis_code_value(value: Optional[str]) -> Optional[str]:
    """TRY_PARSE common OBIS textual and six-group dotted representations."""
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    candidate = re.sub(r"(?i)^OBIS\s*[:#-]?\s*", "", candidate)
    candidate = re.sub(r"\s+", "", candidate)

    dotted = re.fullmatch(r"(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})", candidate)
    if dotted:
        a, b, c, d, e, f = (int(part) for part in dotted.groups())
        if all(0 <= part <= 255 for part in (a, b, c, d, e, f)):
            return f"{a}-{b}:{c}.{d}.{e}*{f}"
        return None

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


__all__ = ["normalize_obis_code_value", "normalize_opcua_node_id_value"]
