"""PyFlink text normalization scalar UDFs."""

from __future__ import annotations

from pyflink.table.udf import udf

from flink_etl_udfs.core.text import (
    normalize_unicode_nfc_value,
    normalize_whitespace_value,
    null_if_blank_value,
    trim_value,
)

trim_text = udf(trim_value, input_types=["STRING"], result_type="STRING", deterministic=True)
normalize_whitespace = udf(
    normalize_whitespace_value,
    input_types=["STRING"],
    result_type="STRING",
    deterministic=True,
)
normalize_unicode_nfc = udf(
    normalize_unicode_nfc_value,
    input_types=["STRING"],
    result_type="STRING",
    deterministic=True,
)
null_if_blank = udf(
    null_if_blank_value,
    input_types=["STRING"],
    result_type="STRING",
    deterministic=True,
)

__all__ = [
    "normalize_unicode_nfc",
    "normalize_whitespace",
    "null_if_blank",
    "trim_text",
]
