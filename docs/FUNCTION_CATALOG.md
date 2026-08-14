# Danh mục public PyFlink UDF — standard-first

Version `0.7.0` dùng một public API mới, không giữ compatibility alias. Quy tắc đặt tên:

```text
<standard>_<operation>_<subject>
```

Khi transform không thuộc riêng một chuẩn, dùng namespace theo semantics (`etl_*`, `url_*`, `dns_*`, `ip_*`, `vn_*`, ...), không gắn tên dataset.

Ví dụ migration:

| Tên cũ | Tên public mới |
| --- | --- |
| `etl_normalize_date` | `iso8601_normalize_date` |
| `etl_normalize_iso_datetime` | `iso8601_normalize_datetime_utc` |
| `etl_normalize_currency_code` | `iso4217_normalize_currency_code` |
| `etl_normalize_e164` | `itu_e164_normalize_phone` |
| `finance_normalize_iban` | `iso13616_normalize_iban` |
| `finance_normalize_bic` | `iso9362_normalize_bic` |
| `finance_normalize_lei` | `iso17442_normalize_lei` |
| `health_normalize_fhir_id` | `fhir_normalize_id` |
| `cti_normalize_stix_id` | `stix21_normalize_id` |
| `security_normalize_cve` | `cve_normalize_id` |
| `supply_normalize_gtin` | `gs1_normalize_gtin` |
| `iot_normalize_opcua_node_id` | `opcua_normalize_node_id` |
| `geo_normalize_epsg_code` | `epsg_normalize_code` |
| `publication_normalize_isbn13` | `iso2108_normalize_isbn13` |
| `etl_normalize_uuid` | `rfc9562_normalize_uuid` |
| `net_normalize_urn` | `rfc8141_normalize_urn` |

## Public API

| Function | Tên hiển thị |
| --- | --- |
| `mask_email` | Che email |
| `mask_text` | Che chuỗi dữ liệu |
| `sha256_fingerprint` | SHA-256 – Tạo fingerprint dữ liệu |
| `email_normalize_address` | Email – Chuẩn hóa địa chỉ email |
| `ip_normalize_address` | IP – Chuẩn hóa địa chỉ IPv4/IPv6 |
| `ip_normalize_cidr` | CIDR – Chuẩn hóa mạng IPv4/IPv6 |
| `etl_canonicalize_json` | JSON – Canonical hóa payload |
| `etl_flatten_json` | JSON – Làm phẳng payload lồng nhau |
| `etl_is_valid_json` | JSON – Kiểm tra payload hợp lệ |
| `etl_latin_name_search_key` | Tên Latin – Tạo khóa tìm kiếm không dấu |
| `etl_normalize_address_text` | Địa chỉ – Chuẩn hóa văn bản địa chỉ |
| `etl_normalize_decimal` | Decimal – Chuẩn hóa số thập phân |
| `etl_normalize_identifier_code` | Identifier – Chuẩn hóa mã nghiệp vụ |
| `etl_normalize_null_token` | NULL – Chuẩn hóa textual null token |
| `etl_normalize_person_name` | Tên người – Chuẩn hóa Unicode và khoảng trắng |
| `etl_stable_record_id` | Record ID – Tạo khóa deterministic theo nguồn |
| `url_canonicalize` | URL – Canonical hóa HTTP(S) URL |
| `url_extract_host` | URL – Trích xuất hostname |
| `dns_normalize_domain` | DNS – Chuẩn hóa domain name |
| `url_redact_secrets` | URL – Che credentials và query secrets |
| `git_normalize_repository_url` | Git – Chuẩn hóa repository URL |
| `osint_build_observation_id` | OSINT – Tạo observation ID deterministic |
| `enrich_extract_profile_url` | Enrichment – Trích metadata URL profile |
| `vn_classify_identity_id` | Việt Nam – Phân loại CMND/CCCD theo cấu trúc |
| `vn_classify_tax_id_structure` | Việt Nam – Phân loại cấu trúc mã số thuế |
| `vn_normalize_citizen_id` | Việt Nam – Chuẩn hóa CMND/CCCD |
| `vn_normalize_mobile_phone` | Việt Nam – Chuẩn hóa số di động và đầu số 11→10 |
| `vn_normalize_tax_id` | Việt Nam – Chuẩn hóa mã số thuế |
| `hash_normalize_hex` | Hash – Chuẩn hóa digest hex |
| `hash_classify_type` | Hash – Phân loại MD5/SHA-1/SHA-256/SHA-512 theo digest |
| `iso8601_normalize_date` | ISO 8601 – Chuẩn hóa ngày |
| `iso8601_normalize_datetime_utc` | ISO 8601 – Chuẩn hóa timestamp về UTC |
| `iso4217_normalize_currency_code` | ISO 4217 – Chuẩn hóa mã tiền tệ |
| `itu_e164_normalize_phone` | ITU-T E.164 – Chuẩn hóa số điện thoại quốc tế |
| `iso13616_normalize_iban` | ISO 13616 – Chuẩn hóa và kiểm tra IBAN |
| `iso9362_normalize_bic` | ISO 9362 – Chuẩn hóa BIC/SWIFT |
| `iso20022_normalize_message_type` | ISO 20022 – Chuẩn hóa message identifier |
| `iso17442_normalize_lei` | ISO 17442 – Chuẩn hóa và kiểm tra LEI |
| `fhir_normalize_id` | HL7 FHIR – Chuẩn hóa Resource ID |
| `fhir_normalize_reference` | HL7 FHIR – Chuẩn hóa Reference |
| `hl7v2_normalize_message_type` | HL7 v2 – Chuẩn hóa message type |
| `dicom_normalize_uid` | DICOM – Chuẩn hóa UID |
| `stix21_normalize_id` | STIX 2.1 – Chuẩn hóa object ID |
| `stix21_normalize_type` | STIX 2.1 – Chuẩn hóa object type |
| `mitre_attack_normalize_technique_id` | MITRE ATT&CK – Chuẩn hóa technique ID |
| `cve_normalize_id` | CVE – Chuẩn hóa vulnerability ID |
| `gs1_normalize_gtin` | GS1 – Chuẩn hóa và kiểm tra GTIN |
| `gs1_normalize_sscc` | GS1 – Chuẩn hóa và kiểm tra SSCC |
| `gs1_epcis_normalize_event_type` | GS1 EPCIS – Chuẩn hóa event type |
| `opcua_normalize_node_id` | OPC UA – Chuẩn hóa NodeId |
| `dlms_cosem_normalize_obis_code` | DLMS/COSEM – Chuẩn hóa OBIS code |
| `epsg_normalize_code` | EPSG – Chuẩn hóa CRS code |
| `icao9303_build_document_id` | ICAO Doc 9303 – Tạo khóa giấy tờ đi lại |
| `iso18013_build_driving_licence_id` | ISO/IEC 18013-1 – Tạo khóa bằng lái xe |
| `iso18013_build_mdl_id` | ISO/IEC 18013-5 – Tạo khóa mDL |
| `iso23220_build_eid_id` | ISO/IEC 23220 – Tạo khóa mobile eID/mdoc |
| `iso3166_normalize_alpha3` | ISO 3166-1 – Chuẩn hóa mã quốc gia Alpha-3 |
| `oidc_build_subject_key` | OpenID Connect – Tạo khóa subject theo iss + sub |
| `w3c_activitystreams_normalize_id` | W3C ActivityStreams 2.0 – Chuẩn hóa Object ID/IRI |
| `rfc3986_normalize_uri` | RFC 3986 – Chuẩn hóa URI |
| `iso26324_normalize_doi` | ISO 26324 – Chuẩn hóa DOI |
| `iso3297_normalize_issn` | ISO 3297 – Chuẩn hóa và kiểm tra ISSN |
| `iso2108_normalize_isbn13` | ISO 2108 – Chuẩn hóa ISBN về ISBN-13 |
| `w3c_did_normalize` | W3C DID Core – Chuẩn hóa Decentralized Identifier |
| `rfc9562_normalize_uuid` | RFC 9562 – Chuẩn hóa UUID/GUID |
| `rfc8141_normalize_urn` | RFC 8141 – Chuẩn hóa URN |

Public SQL surface: **66 functions**.

## Đăng ký qua SQL Gateway

`registry.py` không còn là public deployment mechanism. SQL Gateway đăng ký thẳng entrypoint từ `flink_etl_udfs.public_api.PUBLIC_FUNCTIONS` metadata:

```sql
SET 'python.files' = 's3://fusion_center/transform-library/flink_etl_udfs.zip';

CREATE TEMPORARY SYSTEM FUNCTION ISO2108_NORMALIZE_ISBN13
AS 'flink_etl_udfs.udfs.standards.iso2108_normalize_isbn13'
LANGUAGE PYTHON;

SELECT ISO2108_NORMALIZE_ISBN13('0-306-40615-2');
```

## Cleanup 0.7.0

Loại khỏi public API các helper quá mỏng hoặc dễ thay bằng SQL built-in: `digits_only`, `normalize_unicode_nfc`, `normalize_whitespace`, `null_if_blank`, `trim_text`, generic percentage/probability/range wrappers, ASN/DNS-record/MIME wrappers, Git hash wrappers, OSINT username wrapper và latitude/longitude range wrappers.

Implementation pure-Python có thể vẫn tồn tại nội bộ nếu được function khác tái sử dụng; chúng không còn là contract SQL public.
