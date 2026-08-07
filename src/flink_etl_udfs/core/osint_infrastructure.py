"""Pure OSINT infrastructure and internet-asset normalization transformations."""

from __future__ import annotations

from typing import Optional

_DNS_RECORD_TYPES = {
    "A",
    "AAAA",
    "CAA",
    "CNAME",
    "DNSKEY",
    "DS",
    "HTTPS",
    "MX",
    "NAPTR",
    "NS",
    "PTR",
    "SOA",
    "SRV",
    "SVCB",
    "TLSA",
    "TXT",
}


def normalize_asn_value(value: Optional[str]) -> Optional[str]:
    """Normalize a 32-bit Autonomous System Number to AS<number> form."""
    if value is None:
        return None

    candidate = value.strip().upper()
    if candidate.startswith("AS"):
        candidate = candidate[2:]

    if not candidate.isdigit():
        return None

    number = int(candidate)
    if not 0 <= number <= 4_294_967_295:
        return None
    return f"AS{number}"


def normalize_dns_record_type_value(value: Optional[str]) -> Optional[str]:
    """Normalize a common DNS resource-record type to uppercase."""
    if value is None:
        return None

    candidate = value.strip().upper()
    return candidate if candidate in _DNS_RECORD_TYPES else None


def normalize_mime_type_value(value: Optional[str]) -> Optional[str]:
    """Normalize a MIME media type while dropping optional parameters."""
    if value is None:
        return None

    media_type = value.split(";", 1)[0].strip().lower()
    if media_type.count("/") != 1:
        return None

    major, minor = media_type.split("/", 1)
    if not major or not minor or any(ch.isspace() for ch in media_type):
        return None
    return media_type


__all__ = [
    "normalize_asn_value",
    "normalize_dns_record_type_value",
    "normalize_mime_type_value",
]
