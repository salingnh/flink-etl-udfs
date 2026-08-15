"""PyFlink scalar UDF wrappers for external enrichment services."""

from flink_etl_udfs.enrichment.profile import extract_profile_url_sync
from flink_etl_udfs.udfs._safe import try_udf

# REST enrichment is nondeterministic. Input conversion/row-data errors become NULL;
# infrastructure failures such as network outages remain visible.
extract_profile_url = try_udf(
    extract_profile_url_sync,
    cast_types=["STRING"],
    result_type="STRING",
    deterministic=False,
)


__all__ = ["extract_profile_url"]
