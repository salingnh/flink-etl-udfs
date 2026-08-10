"""PyFlink scalar UDF wrappers for curated ETL domain packs."""

from __future__ import annotations

from pyflink.table.udf import udf

from flink_etl_udfs.core import common, finance, healthcare, industrial, supply_chain, transport_geo, vietnam


def _s(function):
    return udf(function, input_types=["STRING"], result_type="STRING", deterministic=True)


# P0 generic/common
normalize_null_token = _s(common.normalize_null_token_value)
normalize_iso_datetime = _s(common.normalize_iso_datetime_value)
normalize_date = _s(common.normalize_date_value)
normalize_decimal = _s(common.normalize_decimal_value)
normalize_percentage = _s(common.normalize_percentage_value)
normalize_currency_code = _s(common.normalize_currency_code_value)
normalize_person_name = _s(common.normalize_person_name_value)
latin_name_search_key = _s(common.latin_name_search_key_value)
normalize_identifier_code = _s(common.normalize_identifier_code_value)
normalize_address_text = _s(common.normalize_address_text_value)
canonicalize_json = _s(common.canonicalize_json_value)
flatten_json = _s(common.flatten_json_value)
normalize_e164 = udf(
    common.normalize_e164_value,
    input_types=["STRING", "STRING"],
    result_type="STRING",
    deterministic=True,
)
is_valid_json = udf(
    common.is_valid_json_value,
    input_types=["STRING"],
    result_type="BOOLEAN",
    deterministic=True,
)
quality_is_present = udf(
    common.quality_is_present_value,
    input_types=["STRING"],
    result_type="BOOLEAN",
    deterministic=True,
)
quality_number_in_range = udf(
    common.quality_number_in_range_value,
    input_types=["STRING", "STRING", "STRING"],
    result_type="BOOLEAN",
    deterministic=True,
)
stable_record_id = udf(
    common.stable_record_id_value,
    input_types=["STRING", "STRING"],
    result_type="STRING",
    deterministic=True,
)
normalize_probability = udf(
    common.normalize_probability_value,
    input_types=["STRING"],
    result_type="DOUBLE",
    deterministic=True,
)

# Vietnam-specific: chỉ giữ cấu trúc định danh công dân và mã số thuế.
normalize_vn_citizen_id = _s(vietnam.normalize_vn_citizen_id_value)
classify_vn_identity_id = _s(vietnam.classify_vn_identity_id_value)
normalize_vn_tax_id = _s(vietnam.normalize_vn_tax_id_value)
classify_vn_tax_id_structure = _s(vietnam.classify_vn_tax_id_structure_value)

# Healthcare standards.
normalize_fhir_id = _s(healthcare.normalize_fhir_id_value)
normalize_fhir_reference = _s(healthcare.normalize_fhir_reference_value)
normalize_hl7_message_type = _s(healthcare.normalize_hl7_message_type_value)
normalize_dicom_uid = _s(healthcare.normalize_dicom_uid_value)

# Finance and legal-entity standards.
normalize_iban = _s(finance.normalize_iban_value)
normalize_bic = _s(finance.normalize_bic_value)
normalize_iso20022_message_type = _s(finance.normalize_iso20022_message_type_value)
normalize_lei = _s(finance.normalize_lei_value)

# Supply-chain standards.
normalize_gtin = _s(supply_chain.normalize_gtin_value)
normalize_sscc = _s(supply_chain.normalize_sscc_value)
normalize_epcis_event_type = _s(supply_chain.normalize_epcis_event_type_value)

# Industrial standards.
normalize_opcua_node_id = _s(industrial.normalize_opcua_node_id_value)
normalize_obis_code = _s(industrial.normalize_obis_code_value)

# Geospatial scalar values.
normalize_epsg_code = _s(transport_geo.normalize_epsg_code_value)
normalize_latitude = udf(
    transport_geo.normalize_latitude_value,
    input_types=["STRING"],
    result_type="DOUBLE",
    deterministic=True,
)
normalize_longitude = udf(
    transport_geo.normalize_longitude_value,
    input_types=["STRING"],
    result_type="DOUBLE",
    deterministic=True,
)
