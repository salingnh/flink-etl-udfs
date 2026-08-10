"""PyFlink scalar UDFs for OSINT-specific observation semantics."""

from __future__ import annotations

from pyflink.table.udf import udf

from flink_etl_udfs.core.osint import build_observation_id_value, normalize_username_value

normalize_username = udf(
    normalize_username_value,
    input_types=["STRING"],
    result_type="STRING",
    deterministic=True,
)
build_observation_id = udf(
    build_observation_id_value,
    input_types=["STRING", "STRING", "STRING"],
    result_type="STRING",
    deterministic=True,
)

__all__ = ["build_observation_id", "normalize_username"]
