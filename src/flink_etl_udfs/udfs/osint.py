"""PyFlink scalar UDFs for OSINT-specific observation semantics."""

from __future__ import annotations

from flink_etl_udfs.core.osint import build_observation_id_value
from flink_etl_udfs.udfs._safe import try_udf

build_observation_id = try_udf(
    build_observation_id_value,
    input_types=["STRING", "STRING", "STRING"],
    result_type="STRING",
    deterministic=True,
)

__all__ = ["build_observation_id"]
