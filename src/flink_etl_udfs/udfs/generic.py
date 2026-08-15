"""Curated generic PyFlink UDFs that are not attributed to one external standard."""

from __future__ import annotations

from flink_etl_udfs.core import common
from flink_etl_udfs.udfs._safe import try_udf


def _string_udf(function):
    return try_udf(
        function,
        input_types=["STRING"],
        result_type="STRING",
        deterministic=True,
    )


canonicalize_json = _string_udf(common.canonicalize_json_value)
flatten_json = _string_udf(common.flatten_json_value)
latin_name_search_key = _string_udf(common.latin_name_search_key_value)
normalize_address_text = _string_udf(common.normalize_address_text_value)
normalize_decimal = _string_udf(common.normalize_decimal_value)
normalize_identifier_code = _string_udf(common.normalize_identifier_code_value)
normalize_null_token = _string_udf(common.normalize_null_token_value)
normalize_person_name = _string_udf(common.normalize_person_name_value)

is_valid_json = try_udf(
    common.is_valid_json_value,
    input_types=["STRING"],
    result_type="BOOLEAN",
    deterministic=True,
)
stable_record_id = try_udf(
    common.stable_record_id_value,
    input_types=["STRING", "STRING"],
    result_type="STRING",
    deterministic=True,
)


__all__ = [
    "canonicalize_json",
    "flatten_json",
    "is_valid_json",
    "latin_name_search_key",
    "normalize_address_text",
    "normalize_decimal",
    "normalize_identifier_code",
    "normalize_null_token",
    "normalize_person_name",
    "stable_record_id",
]
