"""Pure IP and network normalization transformations."""

from __future__ import annotations

import ipaddress
from typing import Optional


def normalize_ip_value(value: Optional[str]) -> Optional[str]:
    """Return the canonical compressed form of an IPv4/IPv6 address.

    Invalid values return ``None`` so pipelines can route them to data-quality
    handling instead of raising per-record exceptions.
    """
    if value is None:
        return None

    candidate = value.strip()
    if not candidate:
        return None

    try:
        return ipaddress.ip_address(candidate).compressed
    except ValueError:
        return None


def normalize_cidr_value(value: Optional[str]) -> Optional[str]:
    """Return a canonical CIDR network string, accepting host bits in input."""
    if value is None:
        return None

    candidate = value.strip()
    if not candidate:
        return None

    try:
        return str(ipaddress.ip_network(candidate, strict=False))
    except ValueError:
        return None


__all__ = ["normalize_cidr_value", "normalize_ip_value"]
