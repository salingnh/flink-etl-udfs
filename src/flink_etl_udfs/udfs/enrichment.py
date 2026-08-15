"""PyFlink scalar UDF wrappers for external enrichment services."""

from flink_etl_udfs.enrichment.profile import extract_profile_url_sync
from flink_etl_udfs.udfs._safe import try_udf

# REST enrichment là nondeterministic. Row-data/response-shape errors follow the
# public TRY contract and become NULL; infrastructure errors such as network
# outages remain visible because _safe intentionally does not swallow OSError.
extract_profile_url = try_udf(
    extract_profile_url_sync,
    input_types=["STRING"],
    result_type="STRING",
    deterministic=False,
)


__all__ = ["extract_profile_url"]
