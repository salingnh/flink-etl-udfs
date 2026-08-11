"""Central registration helpers for PyFlink ``TableEnvironment``."""

from __future__ import annotations

from typing import TYPE_CHECKING, Mapping

if TYPE_CHECKING:
    from pyflink.table import TableEnvironment


def _register(table_env: "TableEnvironment", functions: Mapping[str, object]) -> None:
    for name, function in functions.items():
        table_env.create_temporary_system_function(name, function)


def register_default_udfs(table_env: "TableEnvironment") -> None:
    """Register small, stable cross-domain text/privacy/network helpers."""
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
    """Register generic deterministic ETL and data-quality transforms."""
    from flink_etl_udfs.udfs import research_domains as common

    _register(
        table_env,
        {
            "etl_canonicalize_json": common.canonicalize_json,
            "etl_flatten_json": common.flatten_json,
            "etl_is_valid_json": common.is_valid_json,
            "etl_latin_name_search_key": common.latin_name_search_key,
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


def register_internet_udfs(table_env: "TableEnvironment") -> None:
    """Register generic internet, DNS, ASN, MIME, and URL transforms."""
    from flink_etl_udfs.udfs import internet

    _register(
        table_env,
        {
            "net_canonicalize_url": internet.canonicalize_url,
            "net_extract_url_host": internet.extract_url_host,
            "net_normalize_asn": internet.normalize_asn,
            "net_normalize_dns_record_type": internet.normalize_dns_record_type,
            "net_normalize_domain": internet.normalize_domain,
            "net_normalize_mime_type": internet.normalize_mime_type,
            "net_redact_url_secrets": internet.redact_url_secrets,
        },
    )


def register_code_udfs(table_env: "TableEnvironment") -> None:
    """Register source-code repository and Git object identifier transforms."""
    from flink_etl_udfs.udfs import code

    _register(
        table_env,
        {
            "code_classify_git_object_hash": code.classify_git_object_hash,
            "code_normalize_git_object_id": code.normalize_git_object_id,
            "code_normalize_repository_url": code.normalize_repository_url,
        },
    )


def register_osint_udfs(table_env: "TableEnvironment") -> None:
    """Register deterministic transforms whose semantics are specifically OSINT observations."""
    from flink_etl_udfs.udfs import osint

    _register(
        table_env,
        {
            "osint_build_observation_id": osint.build_observation_id,
            "osint_normalize_username": osint.normalize_username,
        },
    )


def register_enrichment_udfs(table_env: "TableEnvironment") -> None:
    """Register nondeterministic external enrichment UDFs such as profile URL extraction."""
    from flink_etl_udfs.udfs import enrichment

    _register(
        table_env,
        {
            "enrich_extract_profile_url": enrichment.extract_profile_url,
        },
    )


def register_vietnam_udfs(table_env: "TableEnvironment") -> None:
    """Register self-contained Vietnam citizen, tax, and mobile-number UDFs."""
    from flink_etl_udfs.udfs import vietnam

    _register(
        table_env,
        {
            "vn_classify_identity_id": vietnam.classify_vn_identity_id,
            "vn_classify_tax_id_structure": vietnam.classify_vn_tax_id_structure,
            "vn_normalize_citizen_id": vietnam.normalize_vn_citizen_id,
            "vn_normalize_mobile_phone": vietnam.normalize_vn_mobile_phone,
            "vn_normalize_tax_id": vietnam.normalize_vn_tax_id,
        },
    )


def register_security_udfs(table_env: "TableEnvironment") -> None:
    """Register generic security identifiers plus STIX/MITRE ATT&CK transforms."""
    from flink_etl_udfs.udfs import security

    _register(
        table_env,
        {
            "cti_normalize_attack_technique_id": security.normalize_attack_technique_id,
            "cti_normalize_stix_id": security.normalize_stix_id,
            "cti_normalize_stix_type": security.normalize_stix_type,
            "security_classify_hash_type": security.classify_hash_type,
            "security_normalize_cve": security.normalize_cve,
            "security_normalize_hex_hash": security.normalize_hex_hash,
        },
    )


def register_healthcare_udfs(table_env: "TableEnvironment") -> None:
    """Register FHIR, HL7 v2, and DICOM identifier transforms."""
    from flink_etl_udfs.udfs import research_domains as healthcare

    _register(
        table_env,
        {
            "health_normalize_dicom_uid": healthcare.normalize_dicom_uid,
            "health_normalize_fhir_id": healthcare.normalize_fhir_id,
            "health_normalize_fhir_reference": healthcare.normalize_fhir_reference,
            "health_normalize_hl7_message_type": healthcare.normalize_hl7_message_type,
        },
    )


def register_finance_udfs(table_env: "TableEnvironment") -> None:
    """Register ISO financial/legal-entity identifier transforms."""
    from flink_etl_udfs.udfs import research_domains as finance

    _register(
        table_env,
        {
            "finance_normalize_bic": finance.normalize_bic,
            "finance_normalize_iban": finance.normalize_iban,
            "finance_normalize_iso20022_message_type": finance.normalize_iso20022_message_type,
            "finance_normalize_lei": finance.normalize_lei,
        },
    )


def register_supply_chain_udfs(table_env: "TableEnvironment") -> None:
    """Register GS1 GTIN, SSCC, and EPCIS event transforms."""
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
    """Register OPC UA and DLMS/COSEM identifier transforms."""
    from flink_etl_udfs.udfs import research_domains as industrial

    _register(
        table_env,
        {
            "iot_normalize_obis_code": industrial.normalize_obis_code,
            "iot_normalize_opcua_node_id": industrial.normalize_opcua_node_id,
        },
    )


def register_geospatial_udfs(table_env: "TableEnvironment") -> None:
    """Register scalar coordinate and EPSG code transforms."""
    from flink_etl_udfs.udfs import research_domains as geospatial

    _register(
        table_env,
        {
            "geo_normalize_epsg_code": geospatial.normalize_epsg_code,
            "geo_normalize_latitude": geospatial.normalize_latitude,
            "geo_normalize_longitude": geospatial.normalize_longitude,
        },
    )


def register_all_udfs(table_env: "TableEnvironment") -> None:
    """Register every currently shipped curated scalar UDF pack."""
    register_default_udfs(table_env)
    register_common_udfs(table_env)
    register_internet_udfs(table_env)
    register_code_udfs(table_env)
    register_osint_udfs(table_env)
    register_enrichment_udfs(table_env)
    register_vietnam_udfs(table_env)
    register_security_udfs(table_env)
    register_healthcare_udfs(table_env)
    register_finance_udfs(table_env)
    register_supply_chain_udfs(table_env)
    register_industrial_udfs(table_env)
    register_geospatial_udfs(table_env)


__all__ = [
    "register_all_udfs",
    "register_code_udfs",
    "register_common_udfs",
    "register_default_udfs",
    "register_enrichment_udfs",
    "register_finance_udfs",
    "register_geospatial_udfs",
    "register_healthcare_udfs",
    "register_industrial_udfs",
    "register_internet_udfs",
    "register_osint_udfs",
    "register_security_udfs",
    "register_supply_chain_udfs",
    "register_vietnam_udfs",
]
