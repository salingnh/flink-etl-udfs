"""PyFlink masking and deterministic fingerprinting scalar UDFs."""

from __future__ import annotations

from pyflink.table.udf import udf

from flink_etl_udfs.core.privacy import (
    mask_email_value,
    mask_text_value,
    sha256_fingerprint_value,
)

sha256_fingerprint = udf(
    sha256_fingerprint_value,
    input_types=["STRING"],
    result_type="STRING",
    deterministic=True,
)

mask_text = udf(
    mask_text_value,
    input_types=["STRING"],
    result_type="STRING",
    deterministic=True,
)

mask_email = udf(
    mask_email_value,
    input_types=["STRING"],
    result_type="STRING",
    deterministic=True,
)

__all__ = [
    "mask_email",
    "mask_text",
    "sha256_fingerprint",
]
