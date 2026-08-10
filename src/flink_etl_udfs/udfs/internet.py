"""PyFlink scalar UDFs for internet, DNS, and URL normalization."""

from __future__ import annotations

from pyflink.table.udf import udf

from flink_etl_udfs.core.internet import (
    canonicalize_url_value,
    extract_url_host_value,
    normalize_asn_value,
    normalize_dns_record_type_value,
    normalize_domain_value,
    normalize_mime_type_value,
    redact_url_secrets_value,
)


def _s(function):
    return udf(function, input_types=["STRING"], result_type="STRING", deterministic=True)


canonicalize_url = _s(canonicalize_url_value)
extract_url_host = _s(extract_url_host_value)
normalize_asn = _s(normalize_asn_value)
normalize_dns_record_type = _s(normalize_dns_record_type_value)
normalize_domain = _s(normalize_domain_value)
normalize_mime_type = _s(normalize_mime_type_value)
redact_url_secrets = _s(redact_url_secrets_value)

__all__ = [
    "canonicalize_url",
    "extract_url_host",
    "normalize_asn",
    "normalize_dns_record_type",
    "normalize_domain",
    "normalize_mime_type",
    "redact_url_secrets",
]
