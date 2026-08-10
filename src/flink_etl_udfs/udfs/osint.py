"""PyFlink scalar UDFs for the curated OSINT domain pack."""

from __future__ import annotations

from pyflink.table.udf import udf

from flink_etl_udfs.core.osint_code import (
    classify_git_object_hash_value,
    normalize_git_object_id_value,
    normalize_repository_url_value,
)
from flink_etl_udfs.core.osint_compliance import normalize_lei_value
from flink_etl_udfs.core.osint_evidence import build_observation_id_value, content_sha256_value
from flink_etl_udfs.core.osint_identity import normalize_username_value
from flink_etl_udfs.core.osint_infrastructure import (
    normalize_asn_value,
    normalize_dns_record_type_value,
    normalize_mime_type_value,
)
from flink_etl_udfs.core.osint_security import (
    classify_hash_type_value,
    normalize_cve_value,
    normalize_hex_hash_value,
)
from flink_etl_udfs.core.osint_web import (
    canonicalize_url_value,
    extract_url_host_value,
    normalize_domain_value,
    redact_url_secrets_value,
)


def _string_udf(function):
    return udf(function, input_types=["STRING"], result_type="STRING", deterministic=True)


normalize_username = _string_udf(normalize_username_value)
normalize_domain = _string_udf(normalize_domain_value)
canonicalize_url = _string_udf(canonicalize_url_value)
extract_url_host = _string_udf(extract_url_host_value)
redact_url_secrets = _string_udf(redact_url_secrets_value)
content_sha256 = _string_udf(content_sha256_value)
normalize_hex_hash = _string_udf(normalize_hex_hash_value)
classify_hash_type = _string_udf(classify_hash_type_value)
normalize_cve = _string_udf(normalize_cve_value)
normalize_asn = _string_udf(normalize_asn_value)
normalize_dns_record_type = _string_udf(normalize_dns_record_type_value)
normalize_mime_type = _string_udf(normalize_mime_type_value)
normalize_lei = _string_udf(normalize_lei_value)
normalize_repository_url = _string_udf(normalize_repository_url_value)
normalize_git_object_id = _string_udf(normalize_git_object_id_value)
classify_git_object_hash = _string_udf(classify_git_object_hash_value)

build_observation_id = udf(
    build_observation_id_value,
    input_types=["STRING", "STRING", "STRING"],
    result_type="STRING",
    deterministic=True,
)

__all__ = [
    "build_observation_id",
    "canonicalize_url",
    "classify_git_object_hash",
    "classify_hash_type",
    "content_sha256",
    "extract_url_host",
    "normalize_asn",
    "normalize_cve",
    "normalize_dns_record_type",
    "normalize_domain",
    "normalize_git_object_id",
    "normalize_hex_hash",
    "normalize_lei",
    "normalize_mime_type",
    "normalize_repository_url",
    "normalize_username",
    "redact_url_secrets",
]
