"""PyFlink identifier normalization scalar UDFs."""

from __future__ import annotations

from pyflink.table.udf import udf

from flink_etl_udfs.core.identifiers import digits_only_value, normalize_email_value

digits_only = udf(
    digits_only_value,
    input_types=["STRING"],
    result_type="STRING",
    deterministic=True,
)
normalize_email = udf(
    normalize_email_value,
    input_types=["STRING"],
    result_type="STRING",
    deterministic=True,
)

__all__ = ["digits_only", "normalize_email"]
