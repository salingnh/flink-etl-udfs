"""PyFlink UDF objects named by the standard they implement."""

from __future__ import annotations

from flink_etl_udfs.core import (
    common,
    finance,
    healthcare,
    industrial,
    security,
    security_standards,
    supply_chain,
    transport_geo,
)
from flink_etl_udfs.core.identity_standards import (
    build_icao9303_document_id_value,
    build_iso18013_driving_licence_id_value,
    build_iso18013_mdl_id_value,
    build_iso23220_eid_id_value,
    build_oidc_subject_key_value,
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
from flink_etl_udfs.udfs._safe import try_udf


def _string_udf(function):
    return try_udf(
        function,
        input_types=["STRING"],
        result_type="STRING",
        deterministic=True,
    )


# ISO / IEC / ITU-T generic exchange standards.
iso8601_normalize_date = _string_udf(common.normalize_date_value)
iso8601_normalize_datetime_utc = _string_udf(common.normalize_iso_datetime_value)
iso4217_normalize_currency_code = _string_udf(common.normalize_currency_code_value)
itu_e164_normalize_phone = try_udf(
    common.normalize_e164_value,
    input_types=["STRING", "STRING"],
    result_type="STRING",
    deterministic=True,
)

# Finance and legal-entity standards.
iso13616_normalize_iban = _string_udf(finance.normalize_iban_value)
iso9362_normalize_bic = _string_udf(finance.normalize_bic_value)
iso20022_normalize_message_type = _string_udf(finance.normalize_iso20022_message_type_value)
iso17442_normalize_lei = _string_udf(finance.normalize_lei_value)

# Healthcare standards.
fhir_normalize_id = _string_udf(healthcare.normalize_fhir_id_value)
fhir_normalize_reference = _string_udf(healthcare.normalize_fhir_reference_value)
hl7v2_normalize_message_type = _string_udf(healthcare.normalize_hl7_message_type_value)
dicom_normalize_uid = _string_udf(healthcare.normalize_dicom_uid_value)

# Security / CTI standards.
stix21_normalize_id = _string_udf(security_standards.normalize_stix_id_value)
stix21_normalize_type = _string_udf(security_standards.normalize_stix_type_value)
mitre_attack_normalize_technique_id = _string_udf(
    security_standards.normalize_attack_technique_id_value
)
cve_normalize_id = _string_udf(security.normalize_cve_value)

# Supply-chain standards.
gs1_normalize_gtin = _string_udf(supply_chain.normalize_gtin_value)
gs1_normalize_sscc = _string_udf(supply_chain.normalize_sscc_value)
gs1_epcis_normalize_event_type = _string_udf(supply_chain.normalize_epcis_event_type_value)

# Industrial / geospatial standards and registries.
opcua_normalize_node_id = _string_udf(industrial.normalize_opcua_node_id_value)
dlms_cosem_normalize_obis_code = _string_udf(industrial.normalize_obis_code_value)
epsg_normalize_code = _string_udf(transport_geo.normalize_epsg_code_value)

# Identity, document, publication, URI and identifier standards.
icao9303_build_document_id = try_udf(
    build_icao9303_document_id_value,
    input_types=["STRING", "STRING"],
    result_type="STRING",
    deterministic=True,
)
iso18013_build_driving_licence_id = try_udf(
    build_iso18013_driving_licence_id_value,
    input_types=["STRING", "STRING", "STRING"],
    result_type="STRING",
    deterministic=True,
)
iso18013_build_mdl_id = try_udf(
    build_iso18013_mdl_id_value,
    input_types=["STRING", "STRING"],
    result_type="STRING",
    deterministic=True,
)
iso23220_build_eid_id = try_udf(
    build_iso23220_eid_id_value,
    input_types=["STRING", "STRING", "STRING"],
    result_type="STRING",
    deterministic=True,
)
iso3166_normalize_alpha3 = _string_udf(normalize_iso3166_alpha3_value)
oidc_build_subject_key = try_udf(
    build_oidc_subject_key_value,
    input_types=["STRING", "STRING"],
    result_type="STRING",
    deterministic=True,
)
w3c_activitystreams_normalize_id = _string_udf(normalize_activitystreams_id_value)
rfc3986_normalize_uri = _string_udf(normalize_rfc3986_uri_value)
iso26324_normalize_doi = _string_udf(normalize_iso26324_doi_value)
iso3297_normalize_issn = _string_udf(normalize_iso3297_issn_value)
iso2108_normalize_isbn13 = _string_udf(normalize_iso2108_isbn13_value)
w3c_did_normalize = _string_udf(normalize_w3c_did_value)
rfc9562_normalize_uuid = _string_udf(normalize_rfc9562_uuid_value)
rfc8141_normalize_urn = _string_udf(normalize_rfc8141_urn_value)


__all__ = [
    "cve_normalize_id",
    "dicom_normalize_uid",
    "dlms_cosem_normalize_obis_code",
    "epsg_normalize_code",
    "fhir_normalize_id",
    "fhir_normalize_reference",
    "gs1_epcis_normalize_event_type",
    "gs1_normalize_gtin",
    "gs1_normalize_sscc",
    "hl7v2_normalize_message_type",
    "icao9303_build_document_id",
    "iso13616_normalize_iban",
    "iso17442_normalize_lei",
    "iso18013_build_driving_licence_id",
    "iso18013_build_mdl_id",
    "iso20022_normalize_message_type",
    "iso2108_normalize_isbn13",
    "iso23220_build_eid_id",
    "iso26324_normalize_doi",
    "iso3166_normalize_alpha3",
    "iso3297_normalize_issn",
    "iso4217_normalize_currency_code",
    "iso8601_normalize_date",
    "iso8601_normalize_datetime_utc",
    "iso9362_normalize_bic",
    "itu_e164_normalize_phone",
    "mitre_attack_normalize_technique_id",
    "oidc_build_subject_key",
    "opcua_normalize_node_id",
    "rfc3986_normalize_uri",
    "rfc8141_normalize_urn",
    "rfc9562_normalize_uuid",
    "stix21_normalize_id",
    "stix21_normalize_type",
    "w3c_activitystreams_normalize_id",
    "w3c_did_normalize",
]
