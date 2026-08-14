"""Curated PyFlink identifier normalization UDFs."""

from __future__ import annotations

from pyflink.table.udf import udf

from flink_etl_udfs.core.identifiers import normalize_email_value

normalize_email = udf(
    normalize_email_value,
    input_types=["STRING"],
    result_type="STRING",
    deterministic=True,
)

__all__ = ["normalize_email"]
