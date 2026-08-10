"""PyFlink scalar UDFs for repository and Git object identifiers."""

from __future__ import annotations

from pyflink.table.udf import udf

from flink_etl_udfs.core.code import (
    classify_git_object_hash_value,
    normalize_git_object_id_value,
    normalize_repository_url_value,
)


def _s(function):
    return udf(function, input_types=["STRING"], result_type="STRING", deterministic=True)


normalize_repository_url = _s(normalize_repository_url_value)
normalize_git_object_id = _s(normalize_git_object_id_value)
classify_git_object_hash = _s(classify_git_object_hash_value)

__all__ = ["classify_git_object_hash", "normalize_git_object_id", "normalize_repository_url"]
