"""Curated PyFlink UDFs for URL and domain normalization."""

from __future__ import annotations

from pyflink.table.udf import udf

from flink_etl_udfs.core.internet import (
    canonicalize_url_value,
    extract_url_host_value,
    normalize_domain_value,
    redact_url_secrets_value,
)


def _string_udf(function):
    return udf(function, input_types=["STRING"], result_type="STRING", deterministic=True)


canonicalize_url = _string_udf(canonicalize_url_value)
extract_url_host = _string_udf(extract_url_host_value)
normalize_domain = _string_udf(normalize_domain_value)
redact_url_secrets = _string_udf(redact_url_secrets_value)

__all__ = [
    "canonicalize_url",
    "extract_url_host",
    "normalize_domain",
    "redact_url_secrets",
]
