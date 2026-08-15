"""PyFlink IP/network normalization scalar UDFs."""

from __future__ import annotations

from flink_etl_udfs.core.network import normalize_cidr_value, normalize_ip_value
from flink_etl_udfs.udfs._safe import try_udf

normalize_ip = try_udf(
    normalize_ip_value,
    input_types=["STRING"],
    result_type="STRING",
    deterministic=True,
)
normalize_cidr = try_udf(
    normalize_cidr_value,
    input_types=["STRING"],
    result_type="STRING",
    deterministic=True,
)

__all__ = ["normalize_cidr", "normalize_ip"]
