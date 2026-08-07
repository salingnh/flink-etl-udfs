"""PyFlink scalar UDF wrappers for the researched P0-P3 domain packs."""

from __future__ import annotations

from pyflink.table.udf import udf

from flink_etl_udfs.core import common, finance, healthcare, industrial, insurance, scientific
from flink_etl_udfs.core import security_standards, supply_chain, transport_geo, vietnam


def _s(function):
    return udf(function, input_types=["STRING"], result_type="STRING", deterministic=True)


# P0 common
normalize_null_token = _s(common.normalize_null_token_value)
normalize_iso_datetime = _s(common.normalize_iso_datetime_value)
normalize_date = _s(common.normalize_date_value)
normalize_decimal = _s(common.normalize_decimal_value)
normalize_percentage = _s(common.normalize_percentage_value)
normalize_currency_code = _s(common.normalize_currency_code_value)
canonicalize_json = _s(common.canonicalize_json_value)
flatten_json = _s(common.flatten_json_value)
normalize_e164 = udf(common.normalize_e164_value, input_types=["STRING", "STRING"], result_type="STRING", deterministic=True)
is_valid_json = udf(common.is_valid_json_value, input_types=["STRING"], result_type="BOOLEAN", deterministic=True)
quality_is_present = udf(common.quality_is_present_value, input_types=["STRING"], result_type="BOOLEAN", deterministic=True)
quality_number_in_range = udf(common.quality_number_in_range_value, input_types=["STRING", "STRING", "STRING"], result_type="BOOLEAN", deterministic=True)
stable_record_id = udf(common.stable_record_id_value, input_types=["STRING", "STRING"], result_type="STRING", deterministic=True)
normalize_probability = udf(common.normalize_probability_value, input_types=["STRING"], result_type="DOUBLE", deterministic=True)

# P1 Vietnam + education
normalize_vn_citizen_id = _s(vietnam.normalize_vn_citizen_id_value)
classify_vn_identity_id = _s(vietnam.classify_vn_identity_id_value)
normalize_vn_tax_id = _s(vietnam.normalize_vn_tax_id_value)
classify_vn_tax_id = _s(vietnam.classify_vn_tax_id_value)
normalize_vn_phone = _s(vietnam.normalize_vn_phone_value)
normalize_vn_name = _s(vietnam.normalize_vn_name_value)
vietnamese_name_search_key = _s(vietnam.vietnamese_name_search_key_value)
normalize_vn_address = _s(vietnam.normalize_vn_address_value)
normalize_school_code = _s(vietnam.normalize_school_code_value)
normalize_teacher_code = _s(vietnam.normalize_teacher_code_value)
normalize_student_code = _s(vietnam.normalize_student_code_value)
normalize_academic_year = _s(vietnam.normalize_academic_year_value)
normalize_sms_brandname = _s(vietnam.normalize_sms_brandname_value)
normalize_bank_account = _s(vietnam.normalize_bank_account_value)
build_entity_blocking_key = udf(vietnam.build_entity_blocking_key_value, input_types=["STRING", "STRING", "STRING"], result_type="STRING", deterministic=True)

# P2 CTI / healthcare / finance / supply chain / IoT / transport / geo
normalize_stix_type = _s(security_standards.normalize_stix_type_value)
normalize_stix_id = _s(security_standards.normalize_stix_id_value)
normalize_attack_technique_id = _s(security_standards.normalize_attack_technique_id_value)
normalize_fhir_id = _s(healthcare.normalize_fhir_id_value)
normalize_fhir_reference = _s(healthcare.normalize_fhir_reference_value)
normalize_hl7_message_type = _s(healthcare.normalize_hl7_message_type_value)
normalize_dicom_uid = _s(healthcare.normalize_dicom_uid_value)
normalize_dicom_modality = _s(healthcare.normalize_dicom_modality_value)
normalize_iban = _s(finance.normalize_iban_value)
normalize_bic = _s(finance.normalize_bic_value)
normalize_iso20022_message_type = _s(finance.normalize_iso20022_message_type_value)
normalize_gtin = _s(supply_chain.normalize_gtin_value)
normalize_sscc = _s(supply_chain.normalize_sscc_value)
normalize_epcis_event_type = _s(supply_chain.normalize_epcis_event_type_value)
normalize_opcua_node_id = _s(industrial.normalize_opcua_node_id_value)
normalize_obis_code = _s(industrial.normalize_obis_code_value)
normalize_telemetry_quality = _s(industrial.normalize_telemetry_quality_value)
normalize_gtfs_id = _s(transport_geo.normalize_gtfs_id_value)
normalize_epsg_code = _s(transport_geo.normalize_epsg_code_value)
normalize_latitude = udf(transport_geo.normalize_latitude_value, input_types=["STRING"], result_type="DOUBLE", deterministic=True)
normalize_longitude = udf(transport_geo.normalize_longitude_value, input_types=["STRING"], result_type="DOUBLE", deterministic=True)

# P3 scientific + insurance
normalize_chromosome = _s(scientific.normalize_chromosome_value)
normalize_dna_sequence = _s(scientific.normalize_dna_sequence_value)
normalize_vcf_genotype = _s(scientific.normalize_vcf_genotype_value)
normalize_cf_standard_name = _s(scientific.normalize_cf_standard_name_value)
normalize_grib_short_name = _s(scientific.normalize_grib_short_name_value)
normalize_fits_keyword = _s(scientific.normalize_fits_keyword_value)
normalize_celestial_frame = _s(scientific.normalize_celestial_frame_value)
normalize_acord_version = _s(insurance.normalize_acord_version_value)
normalize_policy_number = _s(insurance.normalize_policy_number_value)
normalize_coverage_code = _s(insurance.normalize_coverage_code_value)
