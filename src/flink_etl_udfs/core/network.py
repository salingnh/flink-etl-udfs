"""Pure IP and network normalization transformations."""

from __future__ import annotations

import ipaddress
import re
from typing import Optional


def normalize_ip_value(value: Optional[str]) -> Optional[str]:
    """Return canonical compressed IPv4/IPv6 from common textual representations."""
    if value is None:
        return None

    candidate = value.strip()
    if not candidate:
        return None
    if candidate.startswith("[") and candidate.endswith("]"):
        candidate = candidate[1:-1].strip()
    candidate = re.sub(r"(?i)^IPv6:\s*", "", candidate)

    try:
        return ipaddress.ip_address(candidate).compressed
    except ValueError:
        return None


def normalize_cidr_value(value: Optional[str]) -> Optional[str]:
    """Return canonical CIDR, accepting host bits and common netmask notation."""
    if value is None:
        return None

    candidate = value.strip()
    if not candidate:
        return None
    candidate = re.sub(r"\s*/\s*", "/", candidate)

    # Common exports write `address netmask` instead of `address/netmask`.
    netmask_form = re.fullmatch(r"(\S+)\s+((?:\d{1,3}\.){3}\d{1,3})", candidate)
    if netmask_form:
        candidate = f"{netmask_form.group(1)}/{netmask_form.group(2)}"

    try:
        return str(ipaddress.ip_network(candidate, strict=False))
    except ValueError:
        return None


__all__ = ["normalize_cidr_value", "normalize_ip_value"]
