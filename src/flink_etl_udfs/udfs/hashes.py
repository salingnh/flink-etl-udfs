"""Generic cryptographic-digest PyFlink UDFs."""

from __future__ import annotations

from pyflink.table.udf import udf

from flink_etl_udfs.core.security import classify_hash_type_value, normalize_hex_hash_value


def _string_udf(function):
    return udf(function, input_types=["STRING"], result_type="STRING", deterministic=True)


normalize_hex_hash = _string_udf(normalize_hex_hash_value)
classify_hash_type = _string_udf(classify_hash_type_value)

__all__ = ["classify_hash_type", "normalize_hex_hash"]
