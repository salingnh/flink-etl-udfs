from __future__ import annotations

from flink_etl_udfs.core.code import normalize_repository_url_value
from flink_etl_udfs.core.common import (
    canonicalize_json_value,
    flatten_json_value,
    normalize_address_text_value,
    normalize_currency_code_value,
    normalize_date_value,
    normalize_decimal_value,
    normalize_e164_value,
    normalize_identifier_code_value,
    normalize_iso_datetime_value,
    normalize_null_token_value,
    normalize_person_name_value,
)
from flink_etl_udfs.core.finance import (
    normalize_bic_value,
    normalize_iban_value,
    normalize_iso20022_message_type_value,
    normalize_lei_value,
)
from flink_etl_udfs.core.healthcare import (
    normalize_dicom_uid_value,
    normalize_fhir_id_value,
    normalize_fhir_reference_value,
    normalize_hl7_message_type_value,
)
from flink_etl_udfs.core.identifiers import normalize_email_value
from flink_etl_udfs.core.identity_standards import (
    normalize_activitystreams_id_value,
    normalize_iso2108_isbn13_value,
    normalize_iso3166_alpha3_value,
    normalize_iso3297_issn_value,
    normalize_iso26324_doi_value,
    normalize_rfc3986_uri_value,
    normalize_rfc8141_urn_value,
    normalize_rfc9562_uuid_value,
    normalize_w3c_did_value,
)
from flink_etl_udfs.core.industrial import (
    normalize_obis_code_value,
    normalize_opcua_node_id_value,
)
from flink_etl_udfs.core.internet import canonicalize_url_value, normalize_domain_value
from flink_etl_udfs.core.network import normalize_cidr_value, normalize_ip_value
from flink_etl_udfs.core.security import normalize_cve_value, normalize_hex_hash_value
from flink_etl_udfs.core.security_standards import (
    normalize_attack_technique_id_value,
    normalize_stix_id_value,
    normalize_stix_type_value,
)
from flink_etl_udfs.core.supply_chain import (
    normalize_epcis_event_type_value,
    normalize_gtin_value,
    normalize_sscc_value,
)
from flink_etl_udfs.core.transport_geo import normalize_epsg_code_value
from flink_etl_udfs.core.vietnam import (
    normalize_vn_citizen_id_value,
    normalize_vn_mobile_phone_value,
    normalize_vn_tax_id_value,
)
from flink_etl_udfs.normalizer_contracts import NORMALIZER_CONTRACTS

NORMALIZER_IMPLEMENTATIONS = {
    "email_normalize_address": normalize_email_value,
    "ip_normalize_address": normalize_ip_value,
    "ip_normalize_cidr": normalize_cidr_value,
    "etl_canonicalize_json": canonicalize_json_value,
    "etl_flatten_json": flatten_json_value,
    "etl_normalize_address_text": normalize_address_text_value,
    "etl_normalize_decimal": normalize_decimal_value,
    "etl_normalize_identifier_code": normalize_identifier_code_value,
    "etl_normalize_null_token": normalize_null_token_value,
    "etl_normalize_person_name": normalize_person_name_value,
    "url_canonicalize": canonicalize_url_value,
    "dns_normalize_domain": normalize_domain_value,
    "git_normalize_repository_url": normalize_repository_url_value,
    "vn_normalize_citizen_id": normalize_vn_citizen_id_value,
    "vn_normalize_mobile_phone": normalize_vn_mobile_phone_value,
    "vn_normalize_tax_id": normalize_vn_tax_id_value,
    "hash_normalize_hex": normalize_hex_hash_value,
    "iso8601_normalize_date": normalize_date_value,
    "iso8601_normalize_datetime_utc": normalize_iso_datetime_value,
    "iso4217_normalize_currency_code": normalize_currency_code_value,
    "itu_e164_normalize_phone": normalize_e164_value,
    "iso13616_normalize_iban": normalize_iban_value,
    "iso9362_normalize_bic": normalize_bic_value,
    "iso20022_normalize_message_type": normalize_iso20022_message_type_value,
    "iso17442_normalize_lei": normalize_lei_value,
    "fhir_normalize_id": normalize_fhir_id_value,
    "fhir_normalize_reference": normalize_fhir_reference_value,
    "hl7v2_normalize_message_type": normalize_hl7_message_type_value,
    "dicom_normalize_uid": normalize_dicom_uid_value,
    "stix21_normalize_id": normalize_stix_id_value,
    "stix21_normalize_type": normalize_stix_type_value,
    "mitre_attack_normalize_technique_id": normalize_attack_technique_id_value,
    "cve_normalize_id": normalize_cve_value,
    "gs1_normalize_gtin": normalize_gtin_value,
    "gs1_normalize_sscc": normalize_sscc_value,
    "gs1_epcis_normalize_event_type": normalize_epcis_event_type_value,
    "opcua_normalize_node_id": normalize_opcua_node_id_value,
    "dlms_cosem_normalize_obis_code": normalize_obis_code_value,
    "epsg_normalize_code": normalize_epsg_code_value,
    "iso3166_normalize_alpha3": normalize_iso3166_alpha3_value,
    "w3c_activitystreams_normalize_id": normalize_activitystreams_id_value,
    "rfc3986_normalize_uri": normalize_rfc3986_uri_value,
    "iso26324_normalize_doi": normalize_iso26324_doi_value,
    "iso3297_normalize_issn": normalize_iso3297_issn_value,
    "iso2108_normalize_isbn13": normalize_iso2108_isbn13_value,
    "w3c_did_normalize": normalize_w3c_did_value,
    "rfc9562_normalize_uuid": normalize_rfc9562_uuid_value,
    "rfc8141_normalize_urn": normalize_rfc8141_urn_value,
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
