"""Single source of truth for the curated SQL-facing UDF surface.

This module intentionally imports no PyFlink code so documentation/tests/tooling can
inspect the public API without requiring a Flink runtime.
"""

from __future__ import annotations

from typing import Dict, Optional, TypedDict


class PublicFunction(TypedDict):
    name: str
    entrypoint: str
    standard: Optional[str]


def _f(name: str, entrypoint: str, standard: Optional[str] = None) -> PublicFunction:
    return {"name": name, "entrypoint": entrypoint, "standard": standard}


PUBLIC_FUNCTIONS: Dict[str, PublicFunction] = {
    # Privacy / generic identifiers.
    "mask_email": _f("Che email", "flink_etl_udfs.udfs.privacy.mask_email"),
    "mask_text": _f("Che chuỗi dữ liệu", "flink_etl_udfs.udfs.privacy.mask_text"),
    "sha256_fingerprint": _f(
        "SHA-256 – Tạo fingerprint dữ liệu",
        "flink_etl_udfs.udfs.privacy.sha256_fingerprint",
        "SHA-256",
    ),
    "email_normalize_address": _f(
        "Email – Chuẩn hóa địa chỉ email",
        "flink_etl_udfs.udfs.identifiers.normalize_email",
    ),
    "ip_normalize_address": _f(
        "IP – Chuẩn hóa địa chỉ IPv4/IPv6",
        "flink_etl_udfs.udfs.network.normalize_ip",
    ),
    "ip_normalize_cidr": _f(
        "CIDR – Chuẩn hóa mạng IPv4/IPv6",
        "flink_etl_udfs.udfs.network.normalize_cidr",
    ),

    # Generic ETL transforms that are deliberately not attributed to one standard.
    "etl_canonicalize_json": _f(
        "JSON – Canonical hóa payload",
        "flink_etl_udfs.udfs.generic.canonicalize_json",
    ),
    "etl_flatten_json": _f(
        "JSON – Làm phẳng payload lồng nhau",
        "flink_etl_udfs.udfs.generic.flatten_json",
    ),
    "etl_is_valid_json": _f(
        "JSON – Kiểm tra payload hợp lệ",
        "flink_etl_udfs.udfs.generic.is_valid_json",
    ),
    "etl_latin_name_search_key": _f(
        "Tên Latin – Tạo khóa tìm kiếm không dấu",
        "flink_etl_udfs.udfs.generic.latin_name_search_key",
    ),
    "etl_normalize_address_text": _f(
        "Địa chỉ – Chuẩn hóa văn bản địa chỉ",
        "flink_etl_udfs.udfs.generic.normalize_address_text",
    ),
    "etl_normalize_decimal": _f(
        "Decimal – Chuẩn hóa số thập phân",
        "flink_etl_udfs.udfs.generic.normalize_decimal",
    ),
    "etl_normalize_identifier_code": _f(
        "Identifier – Chuẩn hóa mã nghiệp vụ",
        "flink_etl_udfs.udfs.generic.normalize_identifier_code",
    ),
    "etl_normalize_null_token": _f(
        "NULL – Chuẩn hóa textual null token",
        "flink_etl_udfs.udfs.generic.normalize_null_token",
    ),
    "etl_normalize_person_name": _f(
        "Tên người – Chuẩn hóa Unicode và khoảng trắng",
        "flink_etl_udfs.udfs.generic.normalize_person_name",
    ),
    "etl_stable_record_id": _f(
        "Record ID – Tạo khóa deterministic theo nguồn",
        "flink_etl_udfs.udfs.generic.stable_record_id",
    ),

    # Internet / source-code / OSINT / controlled enrichment.
    "url_canonicalize": _f(
        "URL – Canonical hóa HTTP(S) URL",
        "flink_etl_udfs.udfs.internet.canonicalize_url",
    ),
    "url_extract_host": _f(
        "URL – Trích xuất hostname",
        "flink_etl_udfs.udfs.internet.extract_url_host",
    ),
    "dns_normalize_domain": _f(
        "DNS – Chuẩn hóa domain name",
        "flink_etl_udfs.udfs.internet.normalize_domain",
    ),
    "url_redact_secrets": _f(
        "URL – Che credentials và query secrets",
        "flink_etl_udfs.udfs.internet.redact_url_secrets",
    ),
    "git_normalize_repository_url": _f(
        "Git – Chuẩn hóa repository URL",
        "flink_etl_udfs.udfs.code.normalize_repository_url",
    ),
    "osint_build_observation_id": _f(
        "OSINT – Tạo observation ID deterministic",
        "flink_etl_udfs.udfs.osint.build_observation_id",
    ),
    "enrich_extract_profile_url": _f(
        "Enrichment – Trích metadata URL profile",
        "flink_etl_udfs.udfs.enrichment.extract_profile_url",
    ),

    # Vietnam-specific semantics with no international replacement.
    "vn_classify_identity_id": _f(
        "Việt Nam – Phân loại CMND/CCCD theo cấu trúc",
        "flink_etl_udfs.udfs.vietnam.classify_vn_identity_id",
    ),
    "vn_classify_tax_id_structure": _f(
        "Việt Nam – Phân loại cấu trúc mã số thuế",
        "flink_etl_udfs.udfs.vietnam.classify_vn_tax_id_structure",
    ),
    "vn_normalize_citizen_id": _f(
        "Việt Nam – Chuẩn hóa CMND/CCCD",
        "flink_etl_udfs.udfs.vietnam.normalize_vn_citizen_id",
    ),
    "vn_normalize_mobile_phone": _f(
        "Việt Nam – Chuẩn hóa số di động và đầu số 11→10",
        "flink_etl_udfs.udfs.vietnam.normalize_vn_mobile_phone",
    ),
    "vn_normalize_tax_id": _f(
        "Việt Nam – Chuẩn hóa mã số thuế",
        "flink_etl_udfs.udfs.vietnam.normalize_vn_tax_id",
    ),

    # Generic cryptographic digest helpers retained because no single identifier standard applies.
    "hash_normalize_hex": _f(
        "Hash – Chuẩn hóa digest hex",
        "flink_etl_udfs.udfs.hashes.normalize_hex_hash",
    ),
    "hash_classify_type": _f(
        "Hash – Phân loại MD5/SHA-1/SHA-256/SHA-512 theo digest",
        "flink_etl_udfs.udfs.hashes.classify_hash_type",
    ),

    # ISO / IEC / ITU-T.
    "iso8601_normalize_date": _f(
        "ISO 8601 – Chuẩn hóa ngày",
        "flink_etl_udfs.udfs.standards.iso8601_normalize_date",
        "ISO 8601",
    ),
    "iso8601_normalize_datetime_utc": _f(
        "ISO 8601 – Chuẩn hóa timestamp về UTC",
        "flink_etl_udfs.udfs.standards.iso8601_normalize_datetime_utc",
        "ISO 8601",
    ),
    "iso4217_normalize_currency_code": _f(
        "ISO 4217 – Chuẩn hóa mã tiền tệ",
        "flink_etl_udfs.udfs.standards.iso4217_normalize_currency_code",
        "ISO 4217",
    ),
    "itu_e164_normalize_phone": _f(
        "ITU-T E.164 – Chuẩn hóa số điện thoại quốc tế",
        "flink_etl_udfs.udfs.standards.itu_e164_normalize_phone",
        "ITU-T E.164",
    ),
    "iso13616_normalize_iban": _f(
        "ISO 13616 – Chuẩn hóa và kiểm tra IBAN",
        "flink_etl_udfs.udfs.standards.iso13616_normalize_iban",
        "ISO 13616",
    ),
    "iso9362_normalize_bic": _f(
        "ISO 9362 – Chuẩn hóa BIC/SWIFT",
        "flink_etl_udfs.udfs.standards.iso9362_normalize_bic",
        "ISO 9362",
    ),
    "iso20022_normalize_message_type": _f(
        "ISO 20022 – Chuẩn hóa message identifier",
        "flink_etl_udfs.udfs.standards.iso20022_normalize_message_type",
        "ISO 20022",
    ),
    "iso17442_normalize_lei": _f(
        "ISO 17442 – Chuẩn hóa và kiểm tra LEI",
        "flink_etl_udfs.udfs.standards.iso17442_normalize_lei",
        "ISO 17442",
    ),

    # Healthcare interchange standards.
    "fhir_normalize_id": _f(
        "HL7 FHIR – Chuẩn hóa Resource ID",
        "flink_etl_udfs.udfs.standards.fhir_normalize_id",
        "HL7 FHIR",
    ),
    "fhir_normalize_reference": _f(
        "HL7 FHIR – Chuẩn hóa Reference",
        "flink_etl_udfs.udfs.standards.fhir_normalize_reference",
        "HL7 FHIR",
    ),
    "hl7v2_normalize_message_type": _f(
        "HL7 v2 – Chuẩn hóa message type",
        "flink_etl_udfs.udfs.standards.hl7v2_normalize_message_type",
        "HL7 v2",
    ),
    "dicom_normalize_uid": _f(
        "DICOM – Chuẩn hóa UID",
        "flink_etl_udfs.udfs.standards.dicom_normalize_uid",
        "DICOM",
    ),

    # Security / CTI standards.
    "stix21_normalize_id": _f(
        "STIX 2.1 – Chuẩn hóa object ID",
        "flink_etl_udfs.udfs.standards.stix21_normalize_id",
        "STIX 2.1",
    ),
    "stix21_normalize_type": _f(
        "STIX 2.1 – Chuẩn hóa object type",
        "flink_etl_udfs.udfs.standards.stix21_normalize_type",
        "STIX 2.1",
    ),
    "mitre_attack_normalize_technique_id": _f(
        "MITRE ATT&CK – Chuẩn hóa technique ID",
        "flink_etl_udfs.udfs.standards.mitre_attack_normalize_technique_id",
        "MITRE ATT&CK",
    ),
    "cve_normalize_id": _f(
        "CVE – Chuẩn hóa vulnerability ID",
        "flink_etl_udfs.udfs.standards.cve_normalize_id",
        "CVE",
    ),

    # Supply chain / industrial / geospatial standards and registries.
    "gs1_normalize_gtin": _f(
        "GS1 – Chuẩn hóa và kiểm tra GTIN",
        "flink_etl_udfs.udfs.standards.gs1_normalize_gtin",
        "GS1",
    ),
    "gs1_normalize_sscc": _f(
        "GS1 – Chuẩn hóa và kiểm tra SSCC",
        "flink_etl_udfs.udfs.standards.gs1_normalize_sscc",
        "GS1",
    ),
    "gs1_epcis_normalize_event_type": _f(
        "GS1 EPCIS – Chuẩn hóa event type",
        "flink_etl_udfs.udfs.standards.gs1_epcis_normalize_event_type",
        "GS1 EPCIS",
    ),
    "opcua_normalize_node_id": _f(
        "OPC UA – Chuẩn hóa NodeId",
        "flink_etl_udfs.udfs.standards.opcua_normalize_node_id",
        "OPC UA",
    ),
    "dlms_cosem_normalize_obis_code": _f(
        "DLMS/COSEM – Chuẩn hóa OBIS code",
        "flink_etl_udfs.udfs.standards.dlms_cosem_normalize_obis_code",
        "DLMS/COSEM",
    ),
    "epsg_normalize_code": _f(
        "EPSG – Chuẩn hóa CRS code",
        "flink_etl_udfs.udfs.standards.epsg_normalize_code",
        "EPSG",
    ),

    # New standards supplied by the catalog input.
    "icao9303_build_document_id": _f(
        "ICAO Doc 9303 – Tạo khóa giấy tờ đi lại",
        "flink_etl_udfs.udfs.standards.icao9303_build_document_id",
        "ICAO Doc 9303",
    ),
    "iso18013_build_driving_licence_id": _f(
        "ISO/IEC 18013-1 – Tạo khóa bằng lái xe",
        "flink_etl_udfs.udfs.standards.iso18013_build_driving_licence_id",
        "ISO/IEC 18013-1",
    ),
    "iso18013_build_mdl_id": _f(
        "ISO/IEC 18013-5 – Tạo khóa mDL",
        "flink_etl_udfs.udfs.standards.iso18013_build_mdl_id",
        "ISO/IEC 18013-5",
    ),
    "iso23220_build_eid_id": _f(
        "ISO/IEC 23220 – Tạo khóa mobile eID/mdoc",
        "flink_etl_udfs.udfs.standards.iso23220_build_eid_id",
        "ISO/IEC 23220",
    ),
    "iso3166_normalize_alpha3": _f(
        "ISO 3166-1 – Chuẩn hóa mã quốc gia Alpha-3",
        "flink_etl_udfs.udfs.standards.iso3166_normalize_alpha3",
        "ISO 3166-1",
    ),
    "oidc_build_subject_key": _f(
        "OpenID Connect – Tạo khóa subject theo iss + sub",
        "flink_etl_udfs.udfs.standards.oidc_build_subject_key",
        "OpenID Connect",
    ),
    "w3c_activitystreams_normalize_id": _f(
        "W3C ActivityStreams 2.0 – Chuẩn hóa Object ID/IRI",
        "flink_etl_udfs.udfs.standards.w3c_activitystreams_normalize_id",
        "W3C ActivityStreams 2.0",
    ),
    "rfc3986_normalize_uri": _f(
        "RFC 3986 – Chuẩn hóa URI",
        "flink_etl_udfs.udfs.standards.rfc3986_normalize_uri",
        "RFC 3986",
    ),
    "iso26324_normalize_doi": _f(
        "ISO 26324 – Chuẩn hóa DOI",
        "flink_etl_udfs.udfs.standards.iso26324_normalize_doi",
        "ISO 26324",
    ),
    "iso3297_normalize_issn": _f(
        "ISO 3297 – Chuẩn hóa và kiểm tra ISSN",
        "flink_etl_udfs.udfs.standards.iso3297_normalize_issn",
        "ISO 3297",
    ),
    "iso2108_normalize_isbn13": _f(
        "ISO 2108 – Chuẩn hóa ISBN về ISBN-13",
        "flink_etl_udfs.udfs.standards.iso2108_normalize_isbn13",
        "ISO 2108",
    ),
    "w3c_did_normalize": _f(
        "W3C DID Core – Chuẩn hóa Decentralized Identifier",
        "flink_etl_udfs.udfs.standards.w3c_did_normalize",
        "W3C DID Core",
    ),
    "rfc9562_normalize_uuid": _f(
        "RFC 9562 – Chuẩn hóa UUID/GUID",
        "flink_etl_udfs.udfs.standards.rfc9562_normalize_uuid",
        "RFC 9562",
    ),
    "rfc8141_normalize_urn": _f(
        "RFC 8141 – Chuẩn hóa URN",
        "flink_etl_udfs.udfs.standards.rfc8141_normalize_urn",
        "RFC 8141",
    ),
}


__all__ = ["PUBLIC_FUNCTIONS", "PublicFunction"]
