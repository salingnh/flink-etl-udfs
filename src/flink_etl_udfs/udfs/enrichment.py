"""PyFlink asynchronous UDF wrappers for external enrichment services."""

from __future__ import annotations

from flink_etl_udfs.enrichment.profile import extract_profile_url_value
from pyflink.table.udf import udf


# REST enrichment là nondeterministic và phải chạy dưới async scalar UDF của Flink.
extract_profile_url = udf(
    extract_profile_url_value,
    input_types=["STRING"],
    result_type="STRING",
    deterministic=False,
)


__all__ = ["extract_profile_url"]
