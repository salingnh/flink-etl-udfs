"""PyFlink masking and deterministic fingerprinting scalar UDFs."""

from __future__ import annotations

from flink_etl_udfs.core.privacy import (
    mask_email_value,
    mask_text_value,
    sha256_fingerprint_value,
)
from flink_etl_udfs.udfs._safe import try_udf

sha256_fingerprint = try_udf(
    sha256_fingerprint_value,
    input_types=["STRING"],
    result_type="STRING",
    deterministic=True,
)

mask_text = try_udf(
    mask_text_value,
    input_types=["STRING"],
    result_type="STRING",
    deterministic=True,
)

mask_email = try_udf(
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
