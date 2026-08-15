"""Curated PyFlink identifier normalization UDFs."""

from __future__ import annotations

from flink_etl_udfs.core.identifiers import normalize_email_value
from flink_etl_udfs.udfs._safe import try_udf

normalize_email = try_udf(
    normalize_email_value,
    cast_types=["STRING"],
    result_type="STRING",
    deterministic=True,
)

__all__ = ["normalize_email"]
