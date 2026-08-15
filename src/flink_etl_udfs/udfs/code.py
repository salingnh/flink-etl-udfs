"""Curated PyFlink UDFs for source-code repository identifiers."""

from __future__ import annotations

from flink_etl_udfs.core.code import normalize_repository_url_value
from flink_etl_udfs.udfs._safe import try_udf

normalize_repository_url = try_udf(
    normalize_repository_url_value,
    input_types=["STRING"],
    result_type="STRING",
    deterministic=True,
)

__all__ = ["normalize_repository_url"]
