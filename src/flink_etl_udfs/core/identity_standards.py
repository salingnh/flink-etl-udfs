"""Deterministic identifier transforms tied to named public standards."""

from __future__ import annotations

import re
import uuid
from typing import Optional
from urllib.parse import quote, urlsplit, urlunsplit

from flink_etl_udfs.core.common import normalize_null_token_value

_PERCENT_ESCAPE_RE = re.compile(r"%[0-9A-Fa-f]{2}")
_GENERIC_CODE_RE = re.compile(r"^[A-Z0-9._/-]+$")
_ICAO_DOCUMENT_RE = re.compile(r"^[A-Z0-9<]{1,20}$")
_UUID_TEXT_RE = re.compile(
    r"^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-"
    r"[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}$"
)
_DID_RE = re.compile(r"^did:([A-Za-z0-9]+):(.+)$", re.IGNORECASE)
_URN_RE = re.compile(r"^urn:([A-Za-z0-9][A-Za-z0-9-]{0,31}):(.+)$", re.IGNORECASE)
_DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$", re.IGNORECASE)


def _uppercase_percent_escapes(value: str) -> str:
    return _PERCENT_ESCAPE_RE.sub(lambda match: match.group(0).upper(), value)


def _encoded_component(value: Optional[str]) -> Optional[str]:
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    return quote(candidate, safe="-._~")


def _compact_upper_code(value: Optional[str]) -> Optional[str]:
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    compact = re.sub(r"\s+", "", candidate).upper()
    return compact if _GENERIC_CODE_RE.fullmatch(compact) else None


def build_icao9303_document_id_value(
    issuer_country: Optional[str], document_number: Optional[str]
) -> Optional[str]:
    """Build a conservative ICAO Doc 9303-oriented travel-document ETL key."""
    issuer = normalize_null_token_value(issuer_country)
    document = normalize_null_token_value(document_number)
    if issuer is None or document is None:
        return None
    issuer = issuer.upper()
    document = re.sub(r"\s+", "", document).upper()
    if not re.fullmatch(r"[A-Z]{3}", issuer):
        return None
    if not _ICAO_DOCUMENT_RE.fullmatch(document):
        return None
    return f"{issuer}:{document}"


def build_iso18013_driving_licence_id_value(
    issuer_country: Optional[str], issuer: Optional[str], licence_number: Optional[str]
) -> Optional[str]:
    """Build a stable driving-licence ETL key using ISO/IEC 18013 identity fields."""
    country = normalize_iso3166_alpha3_value(issuer_country)
    issuer_code = _compact_upper_code(issuer)
    licence = _compact_upper_code(licence_number)
    if country is None or issuer_code is None or licence is None:
        return None
    return f"{country}:{issuer_code}:{licence}"


def build_iso18013_mdl_id_value(
    issuer: Optional[str], document_identifier: Optional[str]
) -> Optional[str]:
    """Build an issuer-scoped canonical ETL key for an ISO/IEC 18013-5 mDL."""
    issuer_value = _encoded_component(issuer)
    document_value = _encoded_component(document_identifier)
    if issuer_value is None or document_value is None:
        return None
    return f"mdl:{issuer_value}:{document_value}"


def build_iso23220_eid_id_value(
    issuer: Optional[str], namespace: Optional[str], document_id: Optional[str]
) -> Optional[str]:
    """Build a canonical ETL key from ISO/IEC 23220 mobile-eID identity components."""
    issuer_value = _encoded_component(issuer)
    namespace_value = _encoded_component(namespace)
    document_value = _encoded_component(document_id)
    if issuer_value is None or namespace_value is None or document_value is None:
        return None
    return f"eid:{issuer_value}:{namespace_value}:{document_value}"


def normalize_iso3166_alpha3_value(value: Optional[str]) -> Optional[str]:
    """Normalize ISO 3166-1 alpha-2 or alpha-3 code to an assigned alpha-3 code."""
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    candidate = candidate.upper()

    import pycountry

    if len(candidate) == 2:
        country = pycountry.countries.get(alpha_2=candidate)
    elif len(candidate) == 3:
        country = pycountry.countries.get(alpha_3=candidate)
    else:
        return None
    return str(country.alpha_3) if country is not None else None


def build_oidc_subject_key_value(issuer: Optional[str], subject_id: Optional[str]) -> Optional[str]:
    """Build an issuer-scoped OpenID Connect subject key from ``iss`` and ``sub``."""
    issuer_value = normalize_null_token_value(issuer)
    subject_value = normalize_null_token_value(subject_id)
    if issuer_value is None or subject_value is None:
        return None
    parsed = urlsplit(issuer_value)
    if not parsed.scheme or not parsed.netloc:
        return None
    return f"oidc:{quote(issuer_value, safe='-._~')}:{quote(subject_value, safe='-._~')}"


def normalize_activitystreams_id_value(value: Optional[str]) -> Optional[str]:
    """Trim and structurally validate an absolute ActivityStreams object IRI."""
    candidate = normalize_null_token_value(value)
    if candidate is None or re.search(r"\s", candidate):
        return None
    parsed = urlsplit(candidate)
    if not parsed.scheme:
        return None
    return candidate


def normalize_rfc3986_uri_value(value: Optional[str]) -> Optional[str]:
    """Normalize an absolute RFC 3986 URI conservatively."""
    candidate = normalize_null_token_value(value)
    if candidate is None or re.search(r"\s", candidate):
        return None
    parsed = urlsplit(candidate)
    if not parsed.scheme:
        return None

    scheme = parsed.scheme.lower()
    netloc = parsed.netloc
    if netloc:
        try:
            hostname = parsed.hostname
            port = parsed.port
        except ValueError:
            return None
        if hostname is None:
            return None
        userinfo = netloc.rsplit("@", 1)[0] + "@" if "@" in netloc else ""
        host = hostname.lower()
        if ":" in host and not host.startswith("["):
            host = f"[{host}]"
        netloc = userinfo + host + (f":{port}" if port is not None else "")

    return urlunsplit(
        (
            scheme,
            netloc,
            _uppercase_percent_escapes(parsed.path),
            _uppercase_percent_escapes(parsed.query),
            _uppercase_percent_escapes(parsed.fragment),
        )
    )


def normalize_iso26324_doi_value(value: Optional[str]) -> Optional[str]:
    """Normalize an ISO 26324 DOI name without resolving it over the network."""
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    lowered = candidate.casefold()
    if lowered.startswith("doi:"):
        candidate = candidate[4:].strip()
    elif lowered.startswith("https://doi.org/"):
        candidate = candidate[len("https://doi.org/") :]
    elif lowered.startswith("http://doi.org/"):
        candidate = candidate[len("http://doi.org/") :]
    candidate = candidate.strip().casefold()
    return candidate if _DOI_RE.fullmatch(candidate) else None


def normalize_iso3297_issn_value(value: Optional[str]) -> Optional[str]:
    """Normalize and checksum-validate an ISSN according to ISO 3297."""
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    candidate = re.sub(r"(?i)^ISSN\s*", "", candidate)
    compact = re.sub(r"[\s-]+", "", candidate).upper()
    if not re.fullmatch(r"\d{7}[\dX]", compact):
        return None
    total = sum(int(char) * weight for char, weight in zip(compact[:7], range(8, 1, -1)))
    check = (11 - total % 11) % 11
    expected = "X" if check == 10 else str(check)
    if compact[-1] != expected:
        return None
    return f"{compact[:4]}-{compact[4:]}"


def _valid_isbn10(compact: str) -> bool:
    if not re.fullmatch(r"\d{9}[\dX]", compact):
        return False
    values = [int(char) for char in compact[:9]] + [10 if compact[-1] == "X" else int(compact[-1])]
    return sum(value * weight for value, weight in zip(values, range(10, 0, -1))) % 11 == 0


def _isbn13_check_digit(body: str) -> str:
    total = sum(int(char) * (1 if index % 2 == 0 else 3) for index, char in enumerate(body))
    return str((10 - total % 10) % 10)


def normalize_iso2108_isbn13_value(value: Optional[str]) -> Optional[str]:
    """Normalize an ISBN-10 or ISBN-13 to checksum-valid canonical ISBN-13."""
    candidate = normalize_null_token_value(value)
    if candidate is None:
        return None
    candidate = re.sub(r"(?i)^ISBN(?:-1[03])?\s*:?[\s]*", "", candidate)
    compact = re.sub(r"[\s-]+", "", candidate).upper()
    if len(compact) == 10:
        if not _valid_isbn10(compact):
            return None
        body = "978" + compact[:9]
        return body + _isbn13_check_digit(body)
    if len(compact) == 13 and compact.isdigit():
        return compact if compact[-1] == _isbn13_check_digit(compact[:12]) else None
    return None


def normalize_w3c_did_value(value: Optional[str]) -> Optional[str]:
    """Normalize a generic W3C DID without applying method-specific rewrite rules."""
    candidate = normalize_null_token_value(value)
    if candidate is None or re.search(r"\s", candidate):
        return None
    match = _DID_RE.fullmatch(candidate)
    if not match:
        return None
    method, method_specific_id = match.groups()
    if not method_specific_id:
        return None
    return f"did:{method.lower()}:{method_specific_id}"


def normalize_rfc9562_uuid_value(value: Optional[str]) -> Optional[str]:
    """Normalize an RFC 9562 UUID/GUID string to lowercase canonical text."""
    candidate = normalize_null_token_value(value)
    if candidate is None or not _UUID_TEXT_RE.fullmatch(candidate):
        return None
    try:
        return str(uuid.UUID(candidate))
    except ValueError:
        return None


def normalize_rfc8141_urn_value(value: Optional[str]) -> Optional[str]:
    """Normalize a generic RFC 8141 URN without namespace-specific equivalence rules."""
    candidate = normalize_null_token_value(value)
    if candidate is None or re.search(r"\s", candidate):
        return None
    match = _URN_RE.fullmatch(candidate)
    if not match:
        return None
    nid, nss_and_components = match.groups()
    if nid.startswith("-") or nid.endswith("-"):
        return None
    return f"urn:{nid.lower()}:{_uppercase_percent_escapes(nss_and_components)}"


__all__ = [
    "build_icao9303_document_id_value",
    "build_iso18013_driving_licence_id_value",
    "build_iso18013_mdl_id_value",
    "build_iso23220_eid_id_value",
    "build_oidc_subject_key_value",
    "normalize_activitystreams_id_value",
    "normalize_iso2108_isbn13_value",
    "normalize_iso26324_doi_value",
    "normalize_iso3166_alpha3_value",
    "normalize_iso3297_issn_value",
    "normalize_rfc3986_uri_value",
    "normalize_rfc8141_urn_value",
    "normalize_rfc9562_uuid_value",
    "normalize_w3c_did_value",
]
