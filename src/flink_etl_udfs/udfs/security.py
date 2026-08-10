"""PyFlink scalar UDFs for security identifiers and CTI standards."""

from __future__ import annotations

from pyflink.table.udf import udf

from flink_etl_udfs.core.security import (
    classify_hash_type_value,
    normalize_cve_value,
    normalize_hex_hash_value,
)
from flink_etl_udfs.core.security_standards import (
    normalize_attack_technique_id_value,
    normalize_stix_id_value,
    normalize_stix_type_value,
)


def _s(function):
    return udf(function, input_types=["STRING"], result_type="STRING", deterministic=True)


normalize_hex_hash = _s(normalize_hex_hash_value)
classify_hash_type = _s(classify_hash_type_value)
normalize_cve = _s(normalize_cve_value)
normalize_stix_type = _s(normalize_stix_type_value)
normalize_stix_id = _s(normalize_stix_id_value)
normalize_attack_technique_id = _s(normalize_attack_technique_id_value)

__all__ = [
    "classify_hash_type",
    "normalize_attack_technique_id",
    "normalize_cve",
    "normalize_hex_hash",
    "normalize_stix_id",
    "normalize_stix_type",
]
