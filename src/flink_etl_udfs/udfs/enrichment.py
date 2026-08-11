"""PyFlink UDF wrappers for external enrichment services."""

from __future__ import annotations

from pyflink.table.udf import udf


def _build_extract_profile_url_udf():
    from flink_etl_udfs.enrichment.profile import extract_profile_url_value

    return udf(
        extract_profile_url_value,
        input_types=["STRING"],
        result_type="STRING",
        deterministic=False,
    )


# REST enrichment is nondeterministic and uses a synchronous scalar UDF for Flink 2.2.x SQL.
extract_profile_url = _build_extract_profile_url_udf()


__all__ = ["extract_profile_url"]
