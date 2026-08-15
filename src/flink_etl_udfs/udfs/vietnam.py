"""PyFlink UDFs for Vietnam-specific deterministic transforms."""

from __future__ import annotations

from flink_etl_udfs.core.vietnam import (
    classify_vn_identity_id_value,
    classify_vn_tax_id_structure_value,
    normalize_vn_citizen_id_value,
    normalize_vn_mobile_phone_value,
    normalize_vn_tax_id_value,
)
from flink_etl_udfs.udfs._safe import try_udf


def _string_udf(function):
    return try_udf(
        function,
        cast_types=["STRING"],
        result_type="STRING",
        deterministic=True,
    )


normalize_vn_citizen_id = _string_udf(normalize_vn_citizen_id_value)
classify_vn_identity_id = _string_udf(classify_vn_identity_id_value)
normalize_vn_mobile_phone = _string_udf(normalize_vn_mobile_phone_value)
normalize_vn_tax_id = _string_udf(normalize_vn_tax_id_value)
classify_vn_tax_id_structure = _string_udf(classify_vn_tax_id_structure_value)


__all__ = [
    "classify_vn_identity_id",
    "classify_vn_tax_id_structure",
    "normalize_vn_citizen_id",
    "normalize_vn_mobile_phone",
    "normalize_vn_tax_id",
]
