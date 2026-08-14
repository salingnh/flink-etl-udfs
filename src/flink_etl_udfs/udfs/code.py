"""Curated PyFlink UDFs for source-code repository identifiers."""

from __future__ import annotations

from pyflink.table.udf import udf

from flink_etl_udfs.core.code import normalize_repository_url_value

normalize_repository_url = udf(
    normalize_repository_url_value,
    input_types=["STRING"],
    result_type="STRING",
    deterministic=True,
)

__all__ = ["normalize_repository_url"]
