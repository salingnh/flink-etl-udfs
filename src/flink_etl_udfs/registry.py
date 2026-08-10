"""Central registration helpers for PyFlink ``TableEnvironment``."""

from __future__ import annotations

from typing import TYPE_CHECKING, Mapping

if TYPE_CHECKING:
    from pyflink.table import TableEnvironment


def _register(table_env: "TableEnvironment", functions: Mapping[str, object]) -> None:
    for name, function in functions.items():
        table_env.create_temporary_system_function(name, function)


def register_default_udfs(table_env: "TableEnvironment") -> None:
    """Register the small stable cross-domain UDF set."""
    from flink_etl_udfs.udfs.identifiers import digits_only, normalize_email
    from flink_etl_udfs.udfs.network import normalize_cidr, normalize_ip
    from flink_etl_udfs.udfs.privacy import mask_email, mask_text, sha256_fingerprint
    from flink_etl_udfs.udfs.text import (
        normalize_unicode_nfc,
        normalize_whitespace,
        null_if_blank,
        trim_text,
    )

    _register(
        table_env,
        {
            "digits_only": digits_only,
            "mask_email": mask_email,
            "mask_text": mask_text,
            "normalize_cidr": normalize_cidr,
            "normalize_email": normalize_email,
            "normalize_ip": normalize_ip,
            "normalize_unicode_nfc": normalize_unicode_nfc,
            "normalize_whitespace": normalize_whitespace,
            "null_if_blank": null_if_blank,
            "sha256_fingerprint": sha256_fingerprint,
            "trim_text": trim_text,
        },
    )


def register_common_udfs(table_env: "TableEnvironment") -> None:
    """Register P0 transforms used by most ingestion pipelines."""
    from flink_etl_udfs.udfs import research_domains as common

    _register(
        table_env,
        {
            "etl_canonicalize_json": common.canonicalize_json,
            "etl_flatten_json": common.flatten_json,
            "etl_is_valid_json": common.is_valid_json,
            "etl_latin_name_search_key": common.latin_name_search_key,
            "etl_normalize_account_identifier": common.normalize_account_identifier,
            "etl_normalize_address_text": common.normalize_address_text,
            "etl_normalize_currency_code": common.normalize_currency_code,
            "etl_normalize_date": common.normalize_date,
            "etl_normalize_decimal": common.normalize_decimal,
            "etl_normalize_e164": common.normalize_e164,
            "etl_normalize_identifier_code": common.normalize_identifier_code,
            "etl_normalize_iso_datetime": common.normalize_iso_datetime,
            "etl_normalize_null_token": common.normalize_null_token,
            "etl_normalize_percentage": common.normalize_percentage,
            "etl_normalize_person_name": common.normalize_person_name,
            "etl_normalize_probability": common.normalize_probability,
            "etl_quality_is_present": common.quality_is_present,
            "etl_quality_number_in_range": common.quality_number_in_range,
            "etl_stable_record_id": common.stable_record_id,
        },
    )


def register_osint_udfs(table_env: "TableEnvironment") -> None:
    """Register the OSINT domain UDF pack."""
    from flink_etl_udfs.udfs import osint

    _register(
        table_env,
        {
            "osint_build_observation_id": osint.build_observation_id,
            "osint_canonicalize_url": osint.canonicalize_url,
            "osint_classify_account_identifier": osint.classify_account_identifier,
            "osint_classify_git_object_hash": osint.classify_git_object_hash,
            "osint_classify_hash_type": osint.classify_hash_type,
            "osint_content_sha256": osint.content_sha256,
            "osint_extract_url_host": osint.extract_url_host,
            "osint_normalize_asn": osint.normalize_asn,
            "osint_normalize_confidence": osint.normalize_confidence,
            "osint_normalize_cve": osint.normalize_cve,
            "osint_normalize_dns_record_type": osint.normalize_dns_record_type,
            "osint_normalize_domain": osint.normalize_domain,
            "osint_normalize_entity_type": osint.normalize_entity_type,
            "osint_normalize_exposure_status": osint.normalize_exposure_status,
            "osint_normalize_git_object_id": osint.normalize_git_object_id,
            "osint_normalize_hex_hash": osint.normalize_hex_hash,
            "osint_normalize_lei": osint.normalize_lei,
            "osint_normalize_mime_type": osint.normalize_mime_type,
            "osint_normalize_name_search_key": osint.normalize_name_search_key,
            "osint_normalize_observed_at_utc": osint.normalize_observed_at_utc,
            "osint_normalize_ownership_percentage": osint.normalize_ownership_percentage,
            "osint_normalize_platform": osint.normalize_platform,
            "osint_normalize_profile_url": osint.normalize_profile_url,
            "osint_normalize_repository_url": osint.normalize_repository_url,
            "osint_normalize_username": osint.normalize_username,
            "osint_normalize_verification_status": osint.normalize_verification_status,
            "osint_redact_url_secrets": osint.redact_url_secrets,
        },
    )


def register_vietnam_udfs(table_env: "TableEnvironment") -> None:
    """Register Vietnam citizen/education/banking P1 transforms."""
    from flink_etl_udfs.udfs import research_domains as vietnam

    _register(
        table_env,
        {
            "vn_build_entity_blocking_key": vietnam.build_entity_blocking_key,
            "vn_classify_identity_id": vietnam.classify_vn_identity_id,
            "vn_classify_tax_id": vietnam.classify_vn_tax_id,
            "vn_normalize_academic_year": vietnam.normalize_academic_year,
            "vn_normalize_address": vietnam.normalize_vn_address,
            "vn_normalize_bank_account": vietnam.normalize_bank_account,
            "vn_normalize_citizen_id": vietnam.normalize_vn_citizen_id,
            "vn_normalize_name": vietnam.normalize_vn_name,
            "vn_normalize_phone": vietnam.normalize_vn_phone,
            "vn_normalize_school_code": vietnam.normalize_school_code,
            "vn_normalize_sms_brandname": vietnam.normalize_sms_brandname,
            "vn_normalize_student_code": vietnam.normalize_student_code,
            "vn_normalize_tax_id": vietnam.normalize_vn_tax_id,
            "vn_normalize_teacher_code": vietnam.normalize_teacher_code,
            "vn_name_search_key": vietnam.vietnamese_name_search_key,
        },
    )


def register_security_standard_udfs(table_env: "TableEnvironment") -> None:
    from flink_etl_udfs.udfs import research_domains as security_standards

    _register(
        table_env,
        {
            "cti_normalize_attack_technique_id": security_standards.normalize_attack_technique_id,
            "cti_normalize_stix_id": security_standards.normalize_stix_id,
            "cti_normalize_stix_type": security_standards.normalize_stix_type,
        },
    )


def register_healthcare_udfs(table_env: "TableEnvironment") -> None:
    from flink_etl_udfs.udfs import research_domains as healthcare

    _register(
        table_env,
        {
            "health_normalize_dicom_modality": healthcare.normalize_dicom_modality,
            "health_normalize_dicom_uid": healthcare.normalize_dicom_uid,
            "health_normalize_fhir_id": healthcare.normalize_fhir_id,
            "health_normalize_fhir_reference": healthcare.normalize_fhir_reference,
            "health_normalize_hl7_message_type": healthcare.normalize_hl7_message_type,
        },
    )


def register_finance_udfs(table_env: "TableEnvironment") -> None:
    from flink_etl_udfs.udfs import research_domains as finance

    _register(
        table_env,
        {
            "finance_normalize_bic": finance.normalize_bic,
            "finance_normalize_iban": finance.normalize_iban,
            "finance_normalize_iso20022_message_type": finance.normalize_iso20022_message_type,
        },
    )


def register_supply_chain_udfs(table_env: "TableEnvironment") -> None:
    from flink_etl_udfs.udfs import research_domains as supply_chain

    _register(
        table_env,
        {
            "supply_normalize_epcis_event_type": supply_chain.normalize_epcis_event_type,
            "supply_normalize_gtin": supply_chain.normalize_gtin,
            "supply_normalize_sscc": supply_chain.normalize_sscc,
        },
    )


def register_industrial_udfs(table_env: "TableEnvironment") -> None:
    from flink_etl_udfs.udfs import research_domains as industrial

    _register(
        table_env,
        {
            "iot_normalize_obis_code": industrial.normalize_obis_code,
            "iot_normalize_opcua_node_id": industrial.normalize_opcua_node_id,
            "iot_normalize_telemetry_quality": industrial.normalize_telemetry_quality,
        },
    )


def register_transport_geo_udfs(table_env: "TableEnvironment") -> None:
    from flink_etl_udfs.udfs import research_domains as transport_geo

    _register(
        table_env,
        {
            "geo_normalize_epsg_code": transport_geo.normalize_epsg_code,
            "geo_normalize_latitude": transport_geo.normalize_latitude,
            "geo_normalize_longitude": transport_geo.normalize_longitude,
            "gtfs_normalize_id": transport_geo.normalize_gtfs_id,
        },
    )


def register_scientific_udfs(table_env: "TableEnvironment") -> None:
    from flink_etl_udfs.udfs import research_domains as scientific

    _register(
        table_env,
        {
            "astro_normalize_celestial_frame": scientific.normalize_celestial_frame,
            "astro_normalize_fits_keyword": scientific.normalize_fits_keyword,
            "climate_normalize_cf_standard_name": scientific.normalize_cf_standard_name,
            "climate_normalize_grib_short_name": scientific.normalize_grib_short_name,
            "genomics_normalize_chromosome": scientific.normalize_chromosome,
            "genomics_normalize_dna_sequence": scientific.normalize_dna_sequence,
            "genomics_normalize_vcf_genotype": scientific.normalize_vcf_genotype,
        },
    )


def register_insurance_udfs(table_env: "TableEnvironment") -> None:
    from flink_etl_udfs.udfs import research_domains as insurance

    _register(
        table_env,
        {
            "insurance_normalize_acord_version": insurance.normalize_acord_version,
            "insurance_normalize_coverage_code": insurance.normalize_coverage_code,
            "insurance_normalize_policy_number": insurance.normalize_policy_number,
        },
    )


def register_all_udfs(table_env: "TableEnvironment") -> None:
    """Register every currently shipped scalar UDF pack."""
    register_default_udfs(table_env)
    register_common_udfs(table_env)
    register_osint_udfs(table_env)
    register_vietnam_udfs(table_env)
    register_security_standard_udfs(table_env)
    register_healthcare_udfs(table_env)
    register_finance_udfs(table_env)
    register_supply_chain_udfs(table_env)
    register_industrial_udfs(table_env)
    register_transport_geo_udfs(table_env)
    register_scientific_udfs(table_env)
    register_insurance_udfs(table_env)


__all__ = [
    "register_all_udfs",
    "register_common_udfs",
    "register_default_udfs",
    "register_finance_udfs",
    "register_healthcare_udfs",
    "register_industrial_udfs",
    "register_insurance_udfs",
    "register_osint_udfs",
    "register_scientific_udfs",
    "register_security_standard_udfs",
    "register_supply_chain_udfs",
    "register_transport_geo_udfs",
    "register_vietnam_udfs",
]
