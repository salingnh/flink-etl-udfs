"""Export the curated public UDF catalog to Elasticsearch metadata JSON/NDJSON.

The Elasticsearch document schema intentionally stays compatible with the legacy
transform metadata contract. Only ``standard`` and ``error_policy`` are additive,
and ``default_type`` is ``ANY`` because public UDFs perform internal TRY_CAST.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from flink_etl_udfs.public_api import PUBLIC_FUNCTIONS

ARTIFACT_URI = "s3://fusion_center/transform-library/flink_etl_udfs.zip"

PARAMS = {
    "etl_stable_record_id": ["source_system", "natural_key"],
    "osint_build_observation_id": ["source_url", "entity_key", "observed_at"],
    "itu_e164_normalize_phone": ["source_field", "default_country_code"],
    "icao9303_build_document_id": ["issuer_country", "document_number"],
    "iso18013_build_driving_licence_id": ["issuer_country", "issuer", "licence_number"],
    "iso18013_build_mdl_id": ["issuer", "document_identifier"],
    "iso23220_build_eid_id": ["issuer", "namespace", "document_id"],
    "oidc_build_subject_key": ["issuer", "subject_id"],
}

OUTPUTS = {"etl_is_valid_json": "BOOLEAN"}

PARAM_LABELS = {
    "source_field": "Field",
    "source_system": "Source system",
    "natural_key": "Natural key",
    "source_url": "Source URL",
    "entity_key": "Entity key",
    "observed_at": "Observed at",
    "default_country_code": "Default country code",
    "issuer_country": "Issuer country",
    "document_number": "Document number",
    "issuer": "Issuer",
    "licence_number": "Licence number",
    "document_identifier": "Document identifier",
    "namespace": "Namespace",
    "document_id": "Document ID",
    "subject_id": "Subject ID",
}

FUNCTION_DESCRIPTIONS = {
    "mask_email": "Che phần local-part của email nhưng giữ domain để vẫn nhận biết được miền email.",
    "mask_text": "Che nội dung chuỗi, giữ ký tự đầu và cuối đối với chuỗi đủ dài.",
    "sha256_fingerprint": "Tạo fingerprint SHA-256 deterministic từ chính chuỗi đầu vào, không tự trim hay biến đổi nội dung trước khi băm.",
    "email_normalize_address": "Trim email, giữ nguyên local-part và chuyển domain về chữ thường; giá trị không có đúng một dấu @ trả NULL.",
    "ip_normalize_address": "Chuẩn hóa địa chỉ IPv4/IPv6 về biểu diễn canonical; địa chỉ không hợp lệ trả NULL.",
    "ip_normalize_cidr": "Chuẩn hóa mạng IPv4/IPv6 dạng CIDR và loại bỏ host bits khỏi địa chỉ mạng.",
    "etl_canonicalize_json": "Parse JSON rồi xuất compact JSON với object keys được sắp xếp ổn định.",
    "etl_flatten_json": "Làm phẳng JSON lồng nhau thành object có dotted/indexed paths để dễ mapping trường dữ liệu.",
    "etl_is_valid_json": "Kiểm tra chuỗi có parse được thành JSON hợp lệ hay không.",
    "etl_latin_name_search_key": "Tạo search/blocking key không dấu, chữ thường cho tên dùng bảng chữ Latin; không dùng làm định danh chính thức.",
    "etl_normalize_address_text": "Chuẩn hóa Unicode, khoảng trắng và spacing quanh dấu phẩy/chấm phẩy của địa chỉ text; không geocode hay suy diễn đơn vị hành chính.",
    "etl_normalize_decimal": "Chuẩn hóa số thập phân bằng Decimal, bỏ leading/trailing zero không cần thiết và tránh sai số binary floating-point.",
    "etl_normalize_identifier_code": "Chuẩn hóa mã nghiệp vụ thành dạng compact uppercase, bỏ whitespace và chỉ giữ syntax A-Z, số, dấu chấm, gạch dưới, slash và hyphen.",
    "etl_normalize_null_token": "Trim chuỗi và chuyển các textual null token phổ biến như null, none, n/a hoặc chuỗi rỗng thành NULL.",
    "etl_normalize_person_name": "Chuẩn hóa tên người theo Unicode NFC và khoảng trắng nhưng giữ nguyên cách viết hoa/thường do nguồn cung cấp.",
    "etl_stable_record_id": "Tạo record ID SHA-256 ổn định từ source system và natural key để hỗ trợ deduplicate/idempotent load.",
    "url_canonicalize": "Canonical hóa HTTP(S) URL, chuẩn hóa host/scheme, loại userinfo, tracking parameters và fragment theo logic hiện tại.",
    "url_extract_host": "Trích hostname canonical từ URL hợp lệ.",
    "dns_normalize_domain": "Chuẩn hóa domain về lowercase IDNA/ASCII, bỏ trailing dot và chuẩn hóa tên miền quốc tế.",
    "url_redact_secrets": "Loại credentials trong authority và che các query parameter nhạy cảm như token trong URL.",
    "git_normalize_repository_url": "Chuẩn hóa repository URL, loại suffix .git và tracking/query không cần thiết.",
    "osint_build_observation_id": "Tạo observation ID SHA-256 ổn định từ source URL, entity key và thời điểm quan sát.",
    "enrich_extract_profile_url": "Gọi profile extraction service để phân tích URL profile và trả metadata profile dạng compact JSON; URL đầu vào không hợp lệ trả NULL.",
    "vn_classify_identity_id": "Phân loại định danh công dân Việt Nam theo cấu trúc 9 chữ số CMND hoặc 12 chữ số CCCD.",
    "vn_classify_tax_id_structure": "Phân loại mã số thuế Việt Nam thành mã cơ sở 10 chữ số hoặc mã mở rộng có hậu tố 3 chữ số.",
    "vn_normalize_citizen_id": "Chuẩn hóa CMND/CCCD Việt Nam về chuỗi chỉ gồm 9 hoặc 12 chữ số, giữ leading zero.",
    "vn_normalize_mobile_phone": "Chuẩn hóa số di động Việt Nam về dạng quốc gia 10 chữ số và chuyển các đầu số di động 11→10 theo đợt chuyển đổi năm 2018.",
    "vn_normalize_tax_id": "Chuẩn hóa mã số thuế Việt Nam về dạng 10 chữ số hoặc 10-3 chữ số.",
    "hash_normalize_hex": "Chuẩn hóa digest hex về lowercase và chỉ chấp nhận độ dài hash phổ biến được hỗ trợ.",
    "hash_classify_type": "Phân loại digest hex theo độ dài thành MD5, SHA-1, SHA-256 hoặc SHA-512.",
    "iso8601_normalize_date": "Chuẩn hóa ngày hợp lệ về dạng YYYY-MM-DD.",
    "iso8601_normalize_datetime_utc": "Chuẩn hóa timestamp có timezone về UTC với hậu tố Z; timestamp không có timezone bị từ chối.",
    "iso4217_normalize_currency_code": "Chuẩn hóa mã tiền tệ 3 chữ cái về uppercase; hàm kiểm tra hình thức mã, không xác nhận membership trong bảng mã hiện hành.",
    "itu_e164_normalize_phone": "Chuẩn hóa số điện thoại về dạng quốc tế bắt đầu bằng + khi đã có country calling code hoặc default country code phù hợp.",
    "iso13616_normalize_iban": "Chuẩn hóa IBAN bằng cách bỏ separator, uppercase và kiểm tra checksum trước khi trả kết quả.",
    "iso9362_normalize_bic": "Chuẩn hóa BIC/SWIFT bằng cách bỏ khoảng trắng, uppercase và kiểm tra cấu trúc 8 hoặc 11 ký tự.",
    "iso20022_normalize_message_type": "Chuẩn hóa ISO 20022 message identifier về lowercase theo syntax message family/version.",
    "iso17442_normalize_lei": "Chuẩn hóa LEI về uppercase và kiểm tra checksum trước khi trả kết quả.",
    "fhir_normalize_id": "Kiểm tra và giữ FHIR Resource id đáp ứng giới hạn ký tự/độ dài của FHIR.",
    "fhir_normalize_reference": "Chuẩn hóa FHIR relative/local Reference như Patient/123 hoặc #contained-id.",
    "hl7v2_normalize_message_type": "Chuẩn hóa HL7 v2 message type về uppercase dạng TYPE^TRIGGER, hỗ trợ thay separator ~ bằng ^.",
    "dicom_normalize_uid": "Kiểm tra DICOM UID/OID dạng numeric dot notation và giới hạn tối đa 64 ký tự.",
    "stix21_normalize_id": "Chuẩn hóa STIX object identifier dạng object-type--UUID và canonical hóa UUID.",
    "stix21_normalize_type": "Chuẩn hóa STIX object type về lowercase hyphenated syntax.",
    "mitre_attack_normalize_technique_id": "Chuẩn hóa MITRE ATT&CK technique/sub-technique ID về uppercase canonical form.",
    "cve_normalize_id": "Chuẩn hóa CVE identifier về dạng CVE-YYYY-NNNN... và loại giá trị sai cấu trúc.",
    "gs1_normalize_gtin": "Chuẩn hóa GTIN và kiểm tra GS1 check digit trước khi trả kết quả.",
    "gs1_normalize_sscc": "Chuẩn hóa SSCC 18 chữ số và kiểm tra GS1 check digit.",
    "gs1_epcis_normalize_event_type": "Chuẩn hóa tên EPCIS event type về canonical event class được hỗ trợ.",
    "opcua_normalize_node_id": "Chuẩn hóa và kiểm tra OPC UA NodeId theo các identifier form được implementation hỗ trợ.",
    "dlms_cosem_normalize_obis_code": "Chuẩn hóa và kiểm tra OBIS code dùng trong DLMS/COSEM metering identifiers.",
    "epsg_normalize_code": "Chuẩn hóa mã CRS về dạng EPSG:<code>; hàm chỉ kiểm tra syntax, không tra registry EPSG trực tuyến.",
    "icao9303_build_document_id": "Tạo khóa ETL ổn định từ issuing country code và travel document number.",
    "iso18013_build_driving_licence_id": "Tạo khóa bằng lái ổn định từ quốc gia phát hành, issuer và licence number.",
    "iso18013_build_mdl_id": "Tạo khóa mDL ổn định theo issuer và document identifier, percent-encode các component cần thiết.",
    "iso23220_build_eid_id": "Tạo khóa mobile eID/mdoc ổn định từ issuer, namespace và document ID.",
    "iso3166_normalize_alpha3": "Tra cứu mã quốc gia ISO 3166-1 alpha-2/alpha-3 và trả mã alpha-3 được gán chính thức trong reference data đóng gói.",
    "oidc_build_subject_key": "Tạo khóa subject ổn định theo cặp issuer (iss) và subject (sub), tránh coi sub là định danh toàn cục độc lập.",
    "w3c_activitystreams_normalize_id": "Trim và kiểm tra ActivityStreams Object ID là một absolute IRI có scheme.",
    "rfc3986_normalize_uri": "Canonical hóa URI tuyệt đối một cách bảo thủ: lowercase scheme/host và uppercase percent-escape hex, không áp dụng equivalence theo từng scheme riêng.",
    "iso26324_normalize_doi": "Loại prefix doi:/doi.org, trim và lowercase DOI name rồi kiểm tra cấu trúc DOI cơ bản.",
    "iso3297_normalize_issn": "Chuẩn hóa ISSN về dạng NNNN-NNNX và kiểm tra checksum ISO 3297.",
    "iso2108_normalize_isbn13": "Chuẩn hóa ISBN-10/ISBN-13 hợp lệ về ISBN-13 13 chữ số và kiểm tra/tính check digit.",
    "w3c_did_normalize": "Chuẩn hóa generic DID bằng cách lowercase scheme/method nhưng không áp dụng rewrite rule riêng của từng DID method.",
    "rfc9562_normalize_uuid": "Chuẩn hóa UUID/GUID textual form về lowercase canonical 8-4-4-4-12.",
    "rfc8141_normalize_urn": "Chuẩn hóa generic URN bằng cách lowercase urn/NID và uppercase hexadecimal trong percent-escape, không áp dụng namespace-specific equivalence.",
}

STANDARD_DESCRIPTIONS = {
    "SHA-256": "SHA-256 là hàm băm mật mã thuộc họ SHA-2, tạo digest 256-bit dùng phổ biến cho fingerprint và kiểm tra toàn vẹn dữ liệu.",
    "ISO 8601": "ISO 8601 là tiêu chuẩn quốc tế quy định cách biểu diễn ngày và thời gian để trao đổi dữ liệu nhất quán.",
    "ISO 4217": "ISO 4217 quy định mã tiền tệ, trong đó alpha code thường là mã ba chữ cái như USD, EUR hoặc VND.",
    "ITU-T E.164": "ITU-T E.164 quy định kế hoạch đánh số viễn thông công cộng quốc tế và giới hạn số quốc tế tối đa 15 chữ số.",
    "ISO 13616": "ISO 13616 quy định IBAN, định danh tài khoản ngân hàng quốc tế có cấu trúc và checksum dùng để phát hiện lỗi nhập liệu.",
    "ISO 9362": "ISO 9362 quy định BIC, mã định danh tổ chức kinh doanh được dùng rộng rãi trong hệ thống tài chính/SWIFT.",
    "ISO 20022": "ISO 20022 là chuẩn mô hình và thông điệp tài chính dùng để trao đổi dữ liệu có cấu trúc giữa các hệ thống tài chính.",
    "ISO 17442": "ISO 17442 quy định Legal Entity Identifier (LEI), mã 20 ký tự dùng để nhận diện pháp nhân tham gia giao dịch tài chính.",
    "HL7 FHIR": "HL7 FHIR là chuẩn trao đổi dữ liệu y tế theo Resource, định nghĩa cả quy tắc cho Resource id và Reference.",
    "HL7 v2": "HL7 v2 là họ chuẩn message-based rất phổ biến trong tích hợp hệ thống y tế và định nghĩa message type/trigger event.",
    "DICOM": "DICOM là chuẩn quốc tế cho dữ liệu và truyền thông hình ảnh y khoa, trong đó UID được dùng để định danh đối tượng DICOM.",
    "STIX 2.1": "STIX 2.1 là chuẩn OASIS để biểu diễn cyber threat intelligence dưới dạng các object và relationship có identifier chuẩn hóa.",
    "MITRE ATT&CK": "MITRE ATT&CK là knowledge base/taxonomy mô tả tactics, techniques và procedures của đối tượng tấn công; technique ID như T1059 hoặc T1059.001 được dùng làm khóa tham chiếu.",
    "CVE": "CVE là hệ thống định danh công khai cho các lỗ hổng bảo mật đã được gán mã CVE duy nhất.",
    "GS1": "GS1 là hệ thống tiêu chuẩn nhận dạng chuỗi cung ứng toàn cầu, bao gồm GTIN cho trade item và SSCC cho logistics unit.",
    "GS1 EPCIS": "GS1 EPCIS là chuẩn chia sẻ visibility event trong chuỗi cung ứng, mô tả các event như ObjectEvent hoặc AggregationEvent.",
    "OPC UA": "OPC UA là chuẩn giao tiếp/interoperability công nghiệp, dùng NodeId để định danh node trong address space.",
    "DLMS/COSEM": "DLMS/COSEM là bộ chuẩn trao đổi dữ liệu đo đếm năng lượng/utility; OBIS code định danh các đại lượng và đối tượng đo.",
    "EPSG": "EPSG Geodetic Parameter Dataset là registry mã hóa coordinate reference systems và các tham số trắc địa, thường được tham chiếu bằng mã EPSG.",
    "ICAO Doc 9303": "ICAO Doc 9303 quy định Machine Readable Travel Documents như hộ chiếu điện tử và các trường nhận dạng liên quan.",
    "ISO/IEC 18013-1": "ISO/IEC 18013-1 quy định các đặc tính vật lý và dữ liệu cốt lõi của driving licence theo chuẩn ISO-compliant.",
    "ISO/IEC 18013-5": "ISO/IEC 18013-5 quy định mobile driving licence (mDL), gồm mô hình dữ liệu và cơ chế trình xuất/xác minh trên thiết bị di động.",
    "ISO/IEC 23220": "ISO/IEC 23220 là họ chuẩn cho mobile eID, tập trung vào định danh điện tử trên thiết bị di động và interoperability của identity documents.",
    "ISO 3166-1": "ISO 3166-1 quy định mã quốc gia alpha-2, alpha-3 và numeric để biểu diễn quốc gia/lãnh thổ nhất quán.",
    "OpenID Connect": "OpenID Connect là identity layer xây trên OAuth 2.0; cặp issuer (iss) và subject (sub) xác định duy nhất một subject trong phạm vi issuer.",
    "W3C ActivityStreams 2.0": "W3C ActivityStreams 2.0 là mô hình dữ liệu để mô tả social activities và objects, trong đó id thường là IRI định danh object.",
    "RFC 3986": "RFC 3986 định nghĩa generic syntax của URI gồm scheme, authority, path, query và fragment.",
    "ISO 26324": "ISO 26324 quy định Digital Object Identifier (DOI), một identifier bền vững cho đối tượng số và tài liệu học thuật.",
    "ISO 3297": "ISO 3297 quy định International Standard Serial Number (ISSN), mã 8 ký tự có check digit cho serial publications.",
    "ISO 2108": "ISO 2108 quy định International Standard Book Number (ISBN), mã định danh cho sách/xuất bản phẩm đơn lẻ với check digit.",
    "W3C DID Core": "W3C DID Core định nghĩa Decentralized Identifier (DID) dạng did:<method>:<method-specific-id> và mô hình DID Document liên quan.",
    "RFC 9562": "RFC 9562 quy định UUID, identifier 128-bit với textual representation canonical và các UUID version hiện hành.",
    "RFC 8141": "RFC 8141 định nghĩa cú pháp Uniform Resource Name (URN), một lớp URI dùng cho identifier theo namespace.",
}

_VALID_SSCC_BODY = "12345678901234567"
_VALID_SSCC_CHECK = str(
    (10 - sum(int(ch) * (3 if index % 2 else 1) for index, ch in enumerate(reversed(_VALID_SSCC_BODY), start=1)) % 10) % 10
)
_VALID_SSCC = _VALID_SSCC_BODY + _VALID_SSCC_CHECK
_STABLE_RECORD_EXAMPLE = hashlib.sha256("crm\x1f123".encode("utf-8")).hexdigest()
_OBSERVATION_EXAMPLE = hashlib.sha256(
    "https://example.com/profile/123\x1fuser:123\x1f2026-08-15T00:00:00Z".encode("utf-8")
).hexdigest()

EXAMPLES = {
    "mask_email": [("alice@example.com", "a***e@example.com"), ("x@example.com", "*@example.com")],
    "mask_text": [("abcdef", "a****f"), ("ab", "**")],
    "sha256_fingerprint": [("abc", "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"), (None, None)],
    "email_normalize_address": [(" User.Name@EXAMPLE.COM ", "User.Name@example.com"), ("not-an-email", None)],
    "ip_normalize_address": [("2001:0db8:0:0:0:0:0:1", "2001:db8::1"), ("999.999.1.1", None)],
    "ip_normalize_cidr": [("192.168.1.14/24", "192.168.1.0/24"), ("192.168.1.1/99", None)],
    "etl_canonicalize_json": [('{"b":2,"a":1}', '{"a":1,"b":2}'), ("{bad json}", None)],
    "etl_flatten_json": [('{"a":{"b":1}}', '{"a.b":1}'), ('{"a":[1,2]}', '{"a[0]":1,"a[1]":2}')],
    "etl_is_valid_json": [('{"a":1}', True), ("{bad json}", False)],
    "etl_latin_name_search_key": [("Đặng Thị Hồng", "dang thi hong"), (" Nguyễn   Văn An ", "nguyen van an")],
    "etl_normalize_address_text": [("12 Nguyễn Trãi,   P. Bến Thành", "12 Nguyễn Trãi, P. Bến Thành"), ("  1 Main St ;  District 1 ", "1 Main St; District 1")],
    "etl_normalize_decimal": [("00123.4500", "123.45"), ("NaN", None)],
    "etl_normalize_identifier_code": [(" hs- 2026 / 001 ", "HS-2026/001"), ("abc@123", None)],
    "etl_normalize_null_token": [(" null ", None), ("  Alice  ", "Alice")],
    "etl_normalize_person_name": [("  Nguyễn   Văn   An  ", "Nguyễn Văn An"), ("  Alice   Smith ", "Alice Smith")],
    "etl_stable_record_id": [(("crm", "123"), _STABLE_RECORD_EXAMPLE), (("", "123"), None)],
    "url_canonicalize": [("HTTPS://user:pass@Example.COM:443/a?utm_source=x&b=2&a=1#section", "https://example.com/a?a=1&b=2"), ("not a url", None)],
    "url_extract_host": [("https://WWW.Example.com/path", "www.example.com"), ("not-a-url", None)],
    "dns_normalize_domain": [("BÜCHER.DE.", "xn--bcher-kva.de"), ("Example.COM.", "example.com")],
    "url_redact_secrets": [("https://user:pass@example.com/api?token=abc&query=data", "https://example.com/api?token=%5BREDACTED%5D&query=data"), ("https://example.com/path", "https://example.com/path")],
    "git_normalize_repository_url": [("https://github.com/salingnh/flink-etl-udfs.git?utm_source=test", "https://github.com/salingnh/flink-etl-udfs"), ("not-a-repository-url", None)],
    "osint_build_observation_id": [(("https://example.com/profile/123", "user:123", "2026-08-15T00:00:00Z"), _OBSERVATION_EXAMPLE), (("", "user:123", "2026-08-15T00:00:00Z"), None)],
    "enrich_extract_profile_url": [("https://facebook.com/sangnv", '{"actor_id":"100001614198876","platform":"facebook",...}'), ("facebook.com/sangnv", None)],
    "vn_classify_identity_id": [("034190006609", "cccd_12"), ("123456789", "cmnd_9")],
    "vn_classify_tax_id_structure": [("0101234567", "base_10"), ("0101234567-001", "extended_13")],
    "vn_normalize_citizen_id": [("034 190 006 609", "034190006609"), ("12345", None)],
    "vn_normalize_mobile_phone": [("0169 123 4567", "0391234567"), ("+84 912 345 678", "0912345678")],
    "vn_normalize_tax_id": [("0101234567001", "0101234567-001"), ("0101234567", "0101234567")],
    "hash_normalize_hex": [("A" * 64, "a" * 64), ("abc123", None)],
    "hash_classify_type": [("A" * 64, "sha256"), ("abc123", None)],
    "iso8601_normalize_date": [("2026-08-15", "2026-08-15"), ("15/08/2026", None)],
    "iso8601_normalize_datetime_utc": [("2026-08-07T09:00:00+07:00", "2026-08-07T02:00:00.000000Z"), ("2026-08-07T09:00:00", None)],
    "iso4217_normalize_currency_code": [("usd", "USD"), ("US", None)],
    "itu_e164_normalize_phone": [(("0912 345 678", "+84"), "+84912345678"), (("123", "+84"), None)],
    "iso13616_normalize_iban": [("GB82 WEST 1234 5698 7654 32", "GB82WEST12345698765432"), ("GB00INVALID", None)],
    "iso9362_normalize_bic": [("deut de ff", "DEUTDEFF"), ("ABC", None)],
    "iso20022_normalize_message_type": [("PACS.008.001.08", "pacs.008.001.08"), ("invalid", None)],
    "iso17442_normalize_lei": [("5493001KJTIIGC8Y1R12", "5493001KJTIIGC8Y1R12"), ("5493001KJTIIGC8Y1R13", None)],
    "fhir_normalize_id": [("patient-001", "patient-001"), ("patient/001", None)],
    "fhir_normalize_reference": [("Patient/patient-001", "Patient/patient-001"), ("patient/patient-001", None)],
    "hl7v2_normalize_message_type": [("adt^a01", "ADT^A01"), ("ADT-A01", None)],
    "dicom_normalize_uid": [("1.2.840.10008.1.2.1", "1.2.840.10008.1.2.1"), ("1..2", None)],
    "stix21_normalize_id": [("indicator--550e8400-e29b-41d4-a716-446655440000", "indicator--550e8400-e29b-41d4-a716-446655440000"), ("Indicator--not-a-uuid", None)],
    "stix21_normalize_type": [(" Threat-Actor ", "threat-actor"), ("Threat Actor", None)],
    "mitre_attack_normalize_technique_id": [("t1059.001", "T1059.001"), ("TA0002", None)],
    "cve_normalize_id": [("cve 2024 12345", "CVE-2024-12345"), ("CVE-24-1", None)],
    "gs1_normalize_gtin": [("4006381333931", "4006381333931"), ("4006381333932", None)],
    "gs1_normalize_sscc": [(_VALID_SSCC, _VALID_SSCC), ("123", None)],
    "gs1_epcis_normalize_event_type": [("object_event", "ObjectEvent"), ("unknown_event", None)],
    "opcua_normalize_node_id": [("ns=2;s=Temperature", "ns=2;s=Temperature"), ("bad-node-id", None)],
    "dlms_cosem_normalize_obis_code": [("1-0:1.8.0*255", "1-0:1.8.0*255"), ("invalid", None)],
    "epsg_normalize_code": [("epsg:4326", "EPSG:4326"), ("EPSG:ABC", None)],
    "icao9303_build_document_id": [(("vnm", " B1234567 "), "VNM:B1234567"), (("VN", "B1234567"), None)],
    "iso18013_build_driving_licence_id": [(("VN", "C06", "12345678901"), "VNM:C06:12345678901"), (("ZZ", "C06", "12345678901"), None)],
    "iso18013_build_mdl_id": [(("https://issuer.example", "mDL-123"), "mdl:https%3A%2F%2Fissuer.example:mDL-123"), (("", "mDL-123"), None)],
    "iso23220_build_eid_id": [(("https://id.example", "national-eid", "123456789"), "eid:https%3A%2F%2Fid.example:national-eid:123456789"), (("", "national-eid", "123456789"), None)],
    "iso3166_normalize_alpha3": [("vn", "VNM"), ("ZZ", None)],
    "oidc_build_subject_key": [(("https://accounts.example.com", "User-123"), "oidc:https%3A%2F%2Faccounts.example.com:User-123"), (("not-an-issuer", "User-123"), None)],
    "w3c_activitystreams_normalize_id": [(" https://social.example/posts/123 ", "https://social.example/posts/123"), ("/posts/123", None)],
    "rfc3986_normalize_uri": [("HTTP://Example.COM/a/%7euser?x=1#Top", "http://example.com/a/%7Euser?x=1#Top"), ("/relative/path", None)],
    "iso26324_normalize_doi": [("https://doi.org/10.1000/ABC123", "10.1000/abc123"), ("doi:abc", None)],
    "iso3297_normalize_issn": [("ISSN 2049 3630", "2049-3630"), ("2049-3631", None)],
    "iso2108_normalize_isbn13": [("0-306-40615-2", "9780306406157"), ("978-0-306-40615-7", "9780306406157")],
    "w3c_did_normalize": [("DID:WEB:example.com:user:123", "did:web:example.com:user:123"), ("did:web:", None)],
    "rfc9562_normalize_uuid": [("550E8400-E29B-41D4-A716-446655440000", "550e8400-e29b-41d4-a716-446655440000"), ("not-a-uuid", None)],
    "rfc8141_normalize_urn": [("URN:EXAMPLE:a123%2cz456", "urn:example:a123%2Cz456"), ("urn::abc", None)],
}


def _format_value(value) -> str:
    if value is None:
        return "NULL"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, tuple):
        return "(" + ", ".join(_format_value(item) for item in value) + ")"
    return json.dumps(value, ensure_ascii=False)


def _description(func_key: str, standard: str | None) -> str:
    lines = ["### Mô tả", FUNCTION_DESCRIPTIONS[func_key]]
    if standard:
        lines.extend(["", "### Chuẩn", STANDARD_DESCRIPTIONS[standard]])
    lines.extend(["", "### Ví dụ"])
    for input_value, output_value in EXAMPLES[func_key]:
        lines.append(
            f"- Input: `{_format_value(input_value)}` → Output: `{_format_value(output_value)}`"
        )
    return "\n".join(lines)


def _config(params: list[str]) -> str:
    result = []
    for index, param in enumerate(params):
        result.append(
            {
                "param_key": param,
                "label": PARAM_LABELS.get(param, param.replace("_", " ").title()),
                "description": f"Input parameter `{param}`.",
                "type": "Text" if param == "default_country_code" else "Field",
                "is_primary": index == 0,
                "is_required": True,
            }
        )
    return json.dumps(result, ensure_ascii=False, separators=(",", ":"))


def build_documents() -> list[dict]:
    missing_descriptions = set(PUBLIC_FUNCTIONS) - set(FUNCTION_DESCRIPTIONS)
    missing_examples = set(PUBLIC_FUNCTIONS) - set(EXAMPLES)
    if missing_descriptions or missing_examples:
        raise RuntimeError(
            f"metadata coverage incomplete: descriptions={sorted(missing_descriptions)}, "
            f"examples={sorted(missing_examples)}"
        )

    docs = []
    for func_key, spec in PUBLIC_FUNCTIONS.items():
        params = PARAMS.get(func_key, ["source_field"])
        output = OUTPUTS.get(func_key, "STRING")
        function_name = func_key.upper()
        placeholders = ", ".join("{{" + param + "}}" for param in params)

        docs.append(
            {
                "func_key": func_key,
                "name": spec["name"],
                "description": _description(func_key, spec["standard"]),
                "params": ",".join(params),
                "category": spec["category"],
                "standard": spec["standard"],
                "default_type": "ANY",
                "output": output,
                "pattern": f"{function_name}({placeholders})",
                "config": _config(params),
                "sql_position": "all",
                "allow_mapping": True,
                "status": 1,
                "type": "flink_sql",
                "error_policy": spec["error_policy"],
                "implementation": {
                    "kind": "python_udf",
                    "function_name": function_name,
                    "entrypoint": spec["entrypoint"],
                    "artifact_uri": ARTIFACT_URI,
                },
            }
        )
    return docs


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out_dir = root / "metadata"
    out_dir.mkdir(parents=True, exist_ok=True)

    docs = build_documents()
    if len(docs) != 66 or len({doc["func_key"] for doc in docs}) != 66:
        raise RuntimeError("expected exactly 66 unique public functions")

    json_path = out_dir / "flink_transform_functions_elastic_v0.7.1.json"
    json_path.write_text(
        json.dumps(docs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    bulk_path = out_dir / "flink_transform_functions_elastic_v0.7.1.bulk.ndjson"
    with bulk_path.open("w", encoding="utf-8") as handle:
        for doc in docs:
            handle.write(json.dumps({"index": {"_id": doc["func_key"]}}) + "\n")
            handle.write(json.dumps(doc, ensure_ascii=False, separators=(",", ":")) + "\n")

    print(json_path)
    print(bulk_path)


if __name__ == "__main__":
    main()
