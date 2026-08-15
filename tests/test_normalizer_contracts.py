from __future__ import annotations

from flink_etl_udfs.core import (
    code,
    common,
    finance,
    healthcare,
    identifiers,
    identity_standards,
    industrial,
    internet,
    network,
    security,
    security_standards,
    supply_chain,
    transport_geo,
    vietnam,
)
from flink_etl_udfs.normalizer_contracts import NORMALIZER_CONTRACTS


NORMALIZER_IMPLEMENTATIONS = {
    "email_normalize_address": identifiers.normalize_email_value,
    "ip_normalize_address": network.normalize_ip_value,
    "ip_normalize_cidr": network.normalize_cidr_value,
    "etl_canonicalize_json": common.canonicalize_json_value,
    "etl_flatten_json": common.flatten_json_value,
    "etl_normalize_address_text": common.normalize_address_text_value,
    "etl_normalize_decimal": common.normalize_decimal_value,
    "etl_normalize_identifier_code": common.normalize_identifier_code_value,
    "etl_normalize_null_token": common.normalize_null_token_value,
    "etl_normalize_person_name": common.normalize_person_name_value,
    "url_canonicalize": internet.canonicalize_url_value,
    "dns_normalize_domain": internet.normalize_domain_value,
    "git_normalize_repository_url": code.normalize_repository_url_value,
    "vn_normalize_citizen_id": vietnam.normalize_vn_citizen_id_value,
    "vn_normalize_mobile_phone": vietnam.normalize_vn_mobile_phone_value,
    "vn_normalize_tax_id": vietnam.normalize_vn_tax_id_value,
    "hash_normalize_hex": security.normalize_hex_hash_value,
    "iso8601_normalize_date": common.normalize_date_value,
    "iso8601_normalize_datetime_utc": common.normalize_iso_datetime_value,
    "iso4217_normalize_currency_code": common.normalize_currency_code_value,
    "itu_e164_normalize_phone": common.normalize_e164_value,
    "iso13616_normalize_iban": finance.normalize_iban_value,
    "iso9362_normalize_bic": finance.normalize_bic_value,
    "iso20022_normalize_message_type": finance.normalize_iso20022_message_type_value,
    "iso17442_normalize_lei": finance.normalize_lei_value,
    "fhir_normalize_id": healthcare.normalize_fhir_id_value,
    "fhir_normalize_reference": healthcare.normalize_fhir_reference_value,
    "hl7v2_normalize_message_type": healthcare.normalize_hl7_message_type_value,
    "dicom_normalize_uid": healthcare.normalize_dicom_uid_value,
    "stix21_normalize_id": security_standards.normalize_stix_id_value,
    "stix21_normalize_type": security_standards.normalize_stix_type_value,
    "mitre_attack_normalize_technique_id": security_standards.normalize_attack_technique_id_value,
    "cve_normalize_id": security.normalize_cve_value,
    "gs1_normalize_gtin": supply_chain.normalize_gtin_value,
    "gs1_normalize_sscc": supply_chain.normalize_sscc_value,
    "gs1_epcis_normalize_event_type": supply_chain.normalize_epcis_event_type_value,
    "opcua_normalize_node_id": industrial.normalize_opcua_node_id_value,
    "dlms_cosem_normalize_obis_code": industrial.normalize_obis_code_value,
    "epsg_normalize_code": transport_geo.normalize_epsg_code_value,
    "iso3166_normalize_alpha3": identity_standards.normalize_iso3166_alpha3_value,
    "w3c_activitystreams_normalize_id": identity_standards.normalize_activitystreams_id_value,
    "rfc3986_normalize_uri": identity_standards.normalize_rfc3986_uri_value,
    "iso26324_normalize_doi": identity_standards.normalize_iso26324_doi_value,
    "iso3297_normalize_issn": identity_standards.normalize_iso3297_issn_value,
    "iso2108_normalize_isbn13": identity_standards.normalize_iso2108_isbn13_value,
    "w3c_did_normalize": identity_standards.normalize_w3c_did_value,
    "rfc9562_normalize_uuid": identity_standards.normalize_rfc9562_uuid_value,
    "rfc8141_normalize_urn": identity_standards.normalize_rfc8141_urn_value,
}


def _as_args(value):
    return value if isinstance(value, tuple) else (value,)


def test_normalizer_contract_implementation_coverage() -> None:
    assert set(NORMALIZER_CONTRACTS) == set(NORMALIZER_IMPLEMENTATIONS)


def test_normalizer_contract_samples() -> None:
    for func_key, contract in NORMALIZER_CONTRACTS.items():
        implementation = NORMALIZER_IMPLEMENTATIONS[func_key]
        assert contract.description.strip()
        assert len(contract.samples) >= 2
        for sample in contract.samples:
            assert implementation(*_as_args(sample.input)) == sample.output, (
                func_key,
                sample,
            )
