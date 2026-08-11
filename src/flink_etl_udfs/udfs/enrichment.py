"""PyFlink scalar UDF wrappers for external enrichment services."""

from pyflink.table.udf import udf

from flink_etl_udfs.enrichment.profile import extract_profile_url_sync

# REST enrichment là nondeterministic nhưng dùng scalar UDF sync trực tiếp để tương thích SQL Gateway 2.2.x.
extract_profile_url = udf(
    extract_profile_url_sync,
    input_types=["STRING"],
    result_type="STRING",
    deterministic=False,
)


__all__ = ["extract_profile_url"]
