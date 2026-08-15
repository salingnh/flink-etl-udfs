"""Executable sample contracts shared by unit tests and Elasticsearch metadata.

Each normalizer is added here only after its implementation supports the documented
representations. Tests execute these exact cases; the metadata exporter renders the
same cases into the public description so runtime and documentation cannot drift.
"""

from __future__ import annotations

from typing import Dict, List, NamedTuple, Union

Scalar = Union[str, int, float, bool, None]
SampleInput = Union[Scalar, tuple[Scalar, ...]]
SampleOutput = Union[str, int, float, bool, None]


class NormalizerSample(NamedTuple):
    input: SampleInput
    output: SampleOutput


class NormalizerContract(NamedTuple):
    description: str
    samples: List[NormalizerSample]


_A64 = "A" * 64
_a64 = "a" * 64
_VALID_SSCC = "123456789012345675"


NORMALIZER_CONTRACTS: Dict[str, NormalizerContract] = {
    "email_normalize_address": NormalizerContract(
        "TRY_PARSE bare email, mailto URI hoặc một display-name angle-bracket form; giữ local-part, IDNA/lowercase domain và trả NULL nếu cấu trúc không xác định an toàn.",
        [
            NormalizerSample(" User.Name@EXAMPLE.COM ", "User.Name@example.com"),
            NormalizerSample("mailto:User.Name@EXAMPLE.COM?subject=Hi", "User.Name@example.com"),
            NormalizerSample("Alice <User@BÜCHER.DE>", "User@xn--bcher-kva.de"),
            NormalizerSample("not-an-email", None),
        ],
    ),
    "ip_normalize_address": NormalizerContract(
        "TRY_PARSE IPv4/IPv6 text, gồm bracketed IPv6 và IPv6: prefix, rồi xuất canonical compressed address.",
        [
            NormalizerSample("2001:0db8:0:0:0:0:0:1", "2001:db8::1"),
            NormalizerSample("[2001:db8::1]", "2001:db8::1"),
            NormalizerSample("IPv6: 2001:db8::1", "2001:db8::1"),
            NormalizerSample("999.999.1.1", None),
        ],
    ),
    "ip_normalize_cidr": NormalizerContract(
        "TRY_PARSE CIDR có host bits, spacing quanh slash hoặc IPv4 address + netmask rồi xuất canonical network/prefix.",
        [
            NormalizerSample("192.168.1.14/24", "192.168.1.0/24"),
            NormalizerSample("192.168.1.14 255.255.255.0", "192.168.1.0/24"),
            NormalizerSample("2001:db8::1 / 64", "2001:db8::/64"),
            NormalizerSample("192.168.1.1/99", None),
        ],
    ),
    "etl_canonicalize_json": NormalizerContract(
        "Parse JSON hợp lệ và xuất compact JSON với object key được sort ổn định; không sửa JSON sai cú pháp bằng heuristic.",
        [
            NormalizerSample('{"b":2,"a":1}', '{"a":1,"b":2}'),
            NormalizerSample(' { "z" : [2,1], "a" : true } ', '{"a":true,"z":[2,1]}'),
            NormalizerSample("{bad json}", None),
        ],
    ),
    "etl_flatten_json": NormalizerContract(
        "Parse JSON lồng nhau và xuất canonical object dùng dotted/indexed paths; JSON sai cú pháp trả NULL.",
        [
            NormalizerSample('{"a":{"b":1}}', '{"a.b":1}'),
            NormalizerSample('{"a":[1,2]}', '{"a[0]":1,"a[1]":2}'),
            NormalizerSample("{bad json}", None),
        ],
    ),
    "etl_normalize_address_text": NormalizerContract(
        "Chuẩn hóa Unicode/whitespace của địa chỉ text và spacing quanh dấu phẩy, chấm phẩy; không suy diễn mã hành chính, postal code hay geocode.",
        [
            NormalizerSample("12 Nguyễn Trãi,   P. Bến Thành", "12 Nguyễn Trãi, P. Bến Thành"),
            NormalizerSample("  1 Main St ;  District 1 ", "1 Main St; District 1"),
            NormalizerSample("null", None),
        ],
    ),
    "etl_normalize_decimal": NormalizerContract(
        "TRY_PARSE số thập phân từ representation dấu chấm/dấu phẩy có thể xác định deterministic, loại grouping separator và xuất decimal text canonical; representation mơ hồ như 1,234 trả NULL thay vì đoán.",
        [
            NormalizerSample("00123.4500", "123.45"),
            NormalizerSample("1.234,50", "1234.5"),
            NormalizerSample("1,234.50", "1234.5"),
            NormalizerSample("1,234", None),
            NormalizerSample("NaN", None),
        ],
    ),
    "etl_normalize_identifier_code": NormalizerContract(
        "Chuẩn hóa business identifier generic bằng cách bỏ whitespace, uppercase và chỉ chấp nhận syntax A-Z, digit, dot, underscore, slash và hyphen.",
        [
            NormalizerSample(" hs- 2026 / 001 ", "HS-2026/001"),
            NormalizerSample("ab.cd_01", "AB.CD_01"),
            NormalizerSample("abc@123", None),
        ],
    ),
    "etl_normalize_null_token": NormalizerContract(
        "Trim input và quy các textual null marker phổ biến về NULL; giá trị text thực được giữ lại sau khi trim.",
        [
            NormalizerSample(" null ", None),
            NormalizerSample("(NULL)", None),
            NormalizerSample("\\N", None),
            NormalizerSample("  Alice  ", "Alice"),
        ],
    ),
    "etl_normalize_person_name": NormalizerContract(
        "Chuẩn hóa tên người theo Unicode NFC và collapse mọi whitespace về một space, đồng thời giữ nguyên letter case và không đoán thứ tự họ/tên.",
        [
            NormalizerSample("  Nguyễn   Văn   An  ", "Nguyễn Văn An"),
            NormalizerSample("Alice\n\tSmith", "Alice Smith"),
            NormalizerSample(" null ", None),
        ],
    ),
    "url_canonicalize": NormalizerContract(
        "TRY_PARSE HTTP(S) URL có hoặc không có scheme khi authority xác định được an toàn, chuẩn hóa host/scheme, bỏ userinfo, tracking params và fragment, sort query để tạo URL canonical.",
        [
            NormalizerSample("HTTPS://user:pass@Example.COM:443/a?utm_source=x&b=2&a=1#section", "https://example.com/a?a=1&b=2"),
            NormalizerSample("www.Example.com/path?b=2&utm_source=x", "https://www.example.com/path?b=2"),
            NormalizerSample("example.com", "https://example.com/"),
            NormalizerSample("not a url", None),
        ],
    ),
    "dns_normalize_domain": NormalizerContract(
        "TRY_PARSE bare DNS name, URL host hoặc email domain rồi xuất lowercase IDNA/ASCII host canonical; domain syntax không hợp lệ trả NULL.",
        [
            NormalizerSample("BÜCHER.DE.", "xn--bcher-kva.de"),
            NormalizerSample("https://WWW.Example.COM/path", "www.example.com"),
            NormalizerSample("User@Example.COM", "example.com"),
            NormalizerSample("-bad.example", None),
        ],
    ),
    "git_normalize_repository_url": NormalizerContract(
        "TRY_PARSE HTTP(S), SSH, git:// và SCP-like Git remote, chuẩn hóa host và bỏ trailing .git/query để trả repository URL ổn định trong cùng transport representation.",
        [
            NormalizerSample("https://github.com/salingnh/flink-etl-udfs.git?utm_source=test", "https://github.com/salingnh/flink-etl-udfs"),
            NormalizerSample("git@github.com:salingnh/flink-etl-udfs.git", "ssh://git@github.com/salingnh/flink-etl-udfs"),
            NormalizerSample("ssh://git@GitHub.com/salingnh/flink-etl-udfs.git", "ssh://git@github.com/salingnh/flink-etl-udfs"),
            NormalizerSample("not-a-repository-url", None),
        ],
    ),
    "vn_normalize_citizen_id": NormalizerContract(
        "TRY_PARSE CMND/CCCD từ label và separator phổ biến, giữ leading zero và chỉ xuất 9 hoặc 12 digit; text lẫn ký tự không được hỗ trợ trả NULL.",
        [
            NormalizerSample("CCCD: 034.190.006.609", "034190006609"),
            NormalizerSample("CMND 123-456-789", "123456789"),
            NormalizerSample("abc034190006609", None),
        ],
    ),
    "vn_normalize_mobile_phone": NormalizerContract(
        "TRY_PARSE số di động Việt Nam từ national/international/tel: representation, bỏ separator và chuyển đầu số 11→10 theo migration map 2018; text/extension không hợp lệ trả NULL.",
        [
            NormalizerSample("0169 123 4567", "0391234567"),
            NormalizerSample("+84 912 345 678", "0912345678"),
            NormalizerSample("tel:+84 (912) 345-678", "0912345678"),
            NormalizerSample("0912FLOWERS", None),
        ],
    ),
    "vn_normalize_tax_id": NormalizerContract(
        "TRY_PARSE mã số thuế Việt Nam từ label và separator phổ biến rồi xuất canonical 10 digits hoặc 10digits-3digits; không xác minh taxpayer registry.",
        [
            NormalizerSample("MST: 0101234567 001", "0101234567-001"),
            NormalizerSample("010.123.4567", "0101234567"),
            NormalizerSample("tax=0101234567", None),
        ],
    ),
    "hash_normalize_hex": NormalizerContract(
        "TRY_PARSE digest hex có algorithm prefix hoặc separator phổ biến, lowercase output và kiểm tra prefix có khớp độ dài MD5/SHA-1/SHA-256/SHA-512 hay không.",
        [
            NormalizerSample("SHA-256: " + _A64, _a64),
            NormalizerSample("MD5: d41d8cd98f00b204e9800998ecf8427e", "d41d8cd98f00b204e9800998ecf8427e"),
            NormalizerSample("MD5: " + _A64, None),
            NormalizerSample("abc123", None),
        ],
    ),
    "iso8601_normalize_date": NormalizerContract(
        "TRY_PARSE các representation ngày phổ biến có thể xác định an toàn và xuất một giá trị canonical YYYY-MM-DD; input không hợp lệ hoặc mơ hồ giữa nhiều date order trả NULL.",
        [
            NormalizerSample("2026-08-15", "2026-08-15"),
            NormalizerSample("15/08/2026", "2026-08-15"),
            NormalizerSample("20260815", "2026-08-15"),
            NormalizerSample("01/02/2026", None),
            NormalizerSample("31/02/2026", None),
        ],
    ),
    "iso8601_normalize_datetime_utc": NormalizerContract(
        "TRY_PARSE các timestamp có timezone từ representation xác định được an toàn rồi canonicalize về UTC với hậu tố Z; không tự đoán timezone và không đoán date order mơ hồ.",
        [
            NormalizerSample("2026-08-15T09:00:00+07:00", "2026-08-15T02:00:00.000000Z"),
            NormalizerSample("15/08/2026 09:00:00+07:00", "2026-08-15T02:00:00.000000Z"),
            NormalizerSample("2026/08/15 09:00 +0700", "2026-08-15T02:00:00.000000Z"),
            NormalizerSample("01/02/2026 09:00:00+07:00", None),
            NormalizerSample("2026-08-15 09:00:00", None),
        ],
    ),
    "iso4217_normalize_currency_code": NormalizerContract(
        "Chuẩn hóa mã tiền tệ ISO 4217 alpha-3 hoặc numeric được gán trong reference data sang alpha-3 canonical; không đoán currency name hoặc symbol mơ hồ.",
        [
            NormalizerSample("vnd", "VND"),
            NormalizerSample("704", "VND"),
            NormalizerSample("ISO 4217: usd", "USD"),
            NormalizerSample("ZZZ", None),
            NormalizerSample("dollar", None),
        ],
    ),
    "itu_e164_normalize_phone": NormalizerContract(
        "TRY_PARSE số điện thoại từ separator phổ biến, prefix +/00/tel: và default country calling code rồi xuất dạng quốc tế +<digits>; extension, vanity text hoặc giá trị không xác định an toàn trả NULL.",
        [
            NormalizerSample(("0912 345 678", "+84"), "+84912345678"),
            NormalizerSample(("tel:+84 (912) 345-678", None), "+84912345678"),
            NormalizerSample(("0084 912 345 678", None), "+84912345678"),
            NormalizerSample(("0912FLOWERS", "+84"), None),
            NormalizerSample(("+84 912 345 678;ext=123", None), None),
        ],
    ),
    "iso13616_normalize_iban": NormalizerContract(
        "TRY_PARSE IBAN label và separator phổ biến, uppercase/compact output rồi kiểm tra mod-97 trước khi trả canonical IBAN.",
        [
            NormalizerSample("GB82 WEST 1234 5698 7654 32", "GB82WEST12345698765432"),
            NormalizerSample("IBAN: GB82-WEST-1234-5698-7654-32", "GB82WEST12345698765432"),
            NormalizerSample("GB82WEST12345698765433", None),
        ],
    ),
    "iso9362_normalize_bic": NormalizerContract(
        "TRY_PARSE BIC/SWIFT label và separator phổ biến, uppercase output và kiểm tra cấu trúc 8 hoặc 11 ký tự.",
        [
            NormalizerSample("deut de ff", "DEUTDEFF"),
            NormalizerSample("SWIFT: deut-de-ff", "DEUTDEFF"),
            NormalizerSample("DEUT DE FF 500", "DEUTDEFF500"),
            NormalizerSample("BAD", None),
        ],
    ),
    "iso20022_normalize_message_type": NormalizerContract(
        "TRY_PARSE ISO 20022 message identifier từ dotted, underscore/hyphen hoặc XSD namespace URN và xuất lowercase dotted canonical identifier.",
        [
            NormalizerSample("PACS.008.001.08", "pacs.008.001.08"),
            NormalizerSample("pacs_008_001_08", "pacs.008.001.08"),
            NormalizerSample("urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08", "pacs.008.001.08"),
            NormalizerSample("pacs.8.1.8", None),
        ],
    ),
    "iso17442_normalize_lei": NormalizerContract(
        "TRY_PARSE LEI label/separator phổ biến, uppercase/compact output và kiểm tra mod-97 trước khi trả canonical 20-character LEI.",
        [
            NormalizerSample("5493001KJTIIGC8Y1R12", "5493001KJTIIGC8Y1R12"),
            NormalizerSample("LEI: 5493-001K-JTII-GC8Y-1R12", "5493001KJTIIGC8Y1R12"),
            NormalizerSample("5493001KJTIIGC8Y1R13", None),
        ],
    ),
    "fhir_normalize_id": NormalizerContract(
        "Chuẩn hóa bare FHIR Resource id hoặc contained-reference #id về id token và kiểm tra character/length constraints của FHIR.",
        [
            NormalizerSample("patient-001", "patient-001"),
            NormalizerSample("#contained-1", "contained-1"),
            NormalizerSample("Patient/123", None),
        ],
    ),
    "fhir_normalize_reference": NormalizerContract(
        "TRY_PARSE FHIR relative/local Reference và urn:uuid representation, canonicalize separator/UUID nhưng không làm mất base URL của absolute cross-server reference.",
        [
            NormalizerSample("Patient / patient-001", "Patient/patient-001"),
            NormalizerSample("#contained-1", "#contained-1"),
            NormalizerSample("urn:uuid:{550E8400-E29B-41D4-A716-446655440000}", "urn:uuid:550e8400-e29b-41d4-a716-446655440000"),
            NormalizerSample("patient-001", None),
        ],
    ),
    "hl7v2_normalize_message_type": NormalizerContract(
        "TRY_PARSE common HL7 v2 message type separators về TYPE^TRIGGER hoặc TYPE^TRIGGER^STRUCTURE canonical uppercase form.",
        [
            NormalizerSample("adt^a01", "ADT^A01"),
            NormalizerSample("ADT-A01", "ADT^A01"),
            NormalizerSample("ADT_A01", "ADT^A01"),
            NormalizerSample("ADT^A01^ADT_A01", "ADT^A01^ADT_A01"),
            NormalizerSample("ADT", None),
        ],
    ),
    "dicom_normalize_uid": NormalizerContract(
        "TRY_PARSE DICOM UID/OID từ bare, OID: hoặc urn:oid: representation, normalize spacing quanh dot và kiểm tra numeric UID syntax/64-character limit.",
        [
            NormalizerSample("1.2.840.10008.1.2.1", "1.2.840.10008.1.2.1"),
            NormalizerSample("urn:oid:1.2.840.10008.1.2.1", "1.2.840.10008.1.2.1"),
            NormalizerSample("OID: 1 . 2 . 840 . 10008 . 1 . 2 . 1", "1.2.840.10008.1.2.1"),
            NormalizerSample("1.02.3", None),
        ],
    ),
    "stix21_normalize_id": NormalizerContract(
        "TRY_PARSE STIX object identifier, canonicalize object type separator/case và UUID wrapper/case rồi xuất type--uuid canonical form.",
        [
            NormalizerSample("indicator--550E8400-E29B-41D4-A716-446655440000", "indicator--550e8400-e29b-41d4-a716-446655440000"),
            NormalizerSample("MALWARE--{550E8400-E29B-41D4-A716-446655440000}", "malware--550e8400-e29b-41d4-a716-446655440000"),
            NormalizerSample("indicator-550e8400-e29b-41d4-a716-446655440000", None),
        ],
    ),
    "stix21_normalize_type": NormalizerContract(
        "Chuẩn hóa STIX object type từ whitespace/underscore/hyphen aliases về lowercase hyphenated token.",
        [
            NormalizerSample("Threat_Actor", "threat-actor"),
            NormalizerSample("threat actor", "threat-actor"),
            NormalizerSample("MALWARE", "malware"),
            NormalizerSample("123-malware", None),
        ],
    ),
    "mitre_attack_normalize_technique_id": NormalizerContract(
        "TRY_PARSE ATT&CK technique/sub-technique ID từ case/prefix/separator aliases và xuất canonical Tdddd hoặc Tdddd.ddd.",
        [
            NormalizerSample("t1059.001", "T1059.001"),
            NormalizerSample("T1059-001", "T1059.001"),
            NormalizerSample("ATT&CK: T1059_001", "T1059.001"),
            NormalizerSample("T159.001", None),
        ],
    ),
    "cve_normalize_id": NormalizerContract(
        "TRY_PARSE CVE prefix và separator aliases rồi xuất canonical CVE-YYYY-NNNN...; không tra trạng thái CVE registry.",
        [
            NormalizerSample("cve 2024 12345", "CVE-2024-12345"),
            NormalizerSample("CVE:2024:12345", "CVE-2024-12345"),
            NormalizerSample("2024-12345", "CVE-2024-12345"),
            NormalizerSample("CVE-24-1", None),
        ],
    ),
    "gs1_normalize_gtin": NormalizerContract(
        "TRY_PARSE GTIN label, GS1 AI (01) và separator phổ biến, compact digits rồi kiểm tra GS1 check digit.",
        [
            NormalizerSample("4006381333931", "4006381333931"),
            NormalizerSample("GTIN: 4006-3813-3393-1", "4006381333931"),
            NormalizerSample("(01)04006381333931", "04006381333931"),
            NormalizerSample("4006381333932", None),
        ],
    ),
    "gs1_normalize_sscc": NormalizerContract(
        "TRY_PARSE SSCC label, GS1 AI (00) và separator phổ biến, compact 18 digits rồi kiểm tra GS1 check digit.",
        [
            NormalizerSample(_VALID_SSCC, _VALID_SSCC),
            NormalizerSample("SSCC: 1234-5678-9012-3456-75", _VALID_SSCC),
            NormalizerSample("(00)" + _VALID_SSCC, _VALID_SSCC),
            NormalizerSample("123456789012345670", None),
        ],
    ),
    "gs1_epcis_normalize_event_type": NormalizerContract(
        "TRY_PARSE EPCIS event class từ snake/kebab/space alias hoặc event-class IRI path và xuất canonical GS1 EPCIS class name.",
        [
            NormalizerSample("object_event", "ObjectEvent"),
            NormalizerSample("aggregation-event", "AggregationEvent"),
            NormalizerSample("https://ref.gs1.org/epcis/TransformationEvent", "TransformationEvent"),
            NormalizerSample("UnknownEvent", None),
        ],
    ),
    "opcua_normalize_node_id": NormalizerContract(
        "TRY_PARSE OPC UA NodeId label/spacing, normalize namespace/index prefixes và canonicalize numeric/GUID/base64 identifier forms.",
        [
            NormalizerSample("ns=2;s=Temperature", "ns=2;s=Temperature"),
            NormalizerSample("NodeId: ns = 2 ; i = 00084", "ns=2;i=84"),
            NormalizerSample("g={550E8400-E29B-41D4-A716-446655440000}", "g=550e8400-e29b-41d4-a716-446655440000"),
            NormalizerSample("ns=70000;i=1", None),
        ],
    ),
    "dlms_cosem_normalize_obis_code": NormalizerContract(
        "TRY_PARSE OBIS label, canonical A-B:C.D.E*F text hoặc six-group dotted representation và xuất canonical textual OBIS form; chỉ kiểm tra structural 0..255 range.",
        [
            NormalizerSample("1-0:1.8.0*255", "1-0:1.8.0*255"),
            NormalizerSample("OBIS: 1 - 0 : 1 . 8 . 0 * 255", "1-0:1.8.0*255"),
            NormalizerSample("1.0.1.8.0.255", "1-0:1.8.0*255"),
            NormalizerSample("1-0:1.8.0*999", None),
        ],
    ),
    "epsg_normalize_code": NormalizerContract(
        "TRY_PARSE EPSG numeric, EPSG: label, OGC CRS URN hoặc OGC definition URL và xuất canonical EPSG:<code>; không xác minh code tồn tại trong registry.",
        [
            NormalizerSample("epsg:4326", "EPSG:4326"),
            NormalizerSample("4326", "EPSG:4326"),
            NormalizerSample("urn:ogc:def:crs:EPSG::4326", "EPSG:4326"),
            NormalizerSample("http://www.opengis.net/def/crs/EPSG/0/4326", "EPSG:4326"),
            NormalizerSample("EPSG:0", None),
        ],
    ),
    "iso3166_normalize_alpha3": NormalizerContract(
        "TRY_PARSE ISO 3166-1 alpha-2, alpha-3, numeric hoặc exact country name qua versioned reference data và xuất assigned alpha-3 canonical code.",
        [
            NormalizerSample("vn", "VNM"),
            NormalizerSample("704", "VNM"),
            NormalizerSample("Viet Nam", "VNM"),
            NormalizerSample("USA", "USA"),
            NormalizerSample("ZZ", None),
        ],
    ),
    "w3c_activitystreams_normalize_id": NormalizerContract(
        "TRY_PARSE bare hoặc angle-bracket absolute IRI dùng làm ActivityStreams Object id; giữ IRI semantics và từ chối relative identifier.",
        [
            NormalizerSample(" https://social.example/posts/123 ", "https://social.example/posts/123"),
            NormalizerSample("<https://social.example/posts/123>", "https://social.example/posts/123"),
            NormalizerSample("/posts/123", None),
        ],
    ),
    "rfc3986_normalize_uri": NormalizerContract(
        "TRY_PARSE absolute URI, normalize scheme/IDNA host và percent-encoding của unreserved characters theo RFC 3986 mà không invent scheme-specific equivalence.",
        [
            NormalizerSample("HTTP://Example.COM/a/%7euser?x=1#Top", "http://example.com/a/~user?x=1#Top"),
            NormalizerSample("<https://BÜCHER.DE/%7Ealice>", "https://xn--bcher-kva.de/~alice"),
            NormalizerSample("/relative/path", None),
        ],
    ),
    "iso26324_normalize_doi": NormalizerContract(
        "TRY_PARSE bare DOI, DOI label hoặc doi.org/dx.doi.org resolver URL rồi xuất lowercase DOI name canonical; không thực hiện network resolution/registry lookup.",
        [
            NormalizerSample("https://doi.org/10.1000/ABC123", "10.1000/abc123"),
            NormalizerSample("DOI: 10.1000/ABC123", "10.1000/abc123"),
            NormalizerSample("https://dx.doi.org/10.1000/ABC123?source=x", "10.1000/abc123"),
            NormalizerSample("doi:abc", None),
        ],
    ),
    "iso3297_normalize_issn": NormalizerContract(
        "TRY_PARSE ISSN/ISSN-L label và separator aliases, kiểm tra ISO 3297 checksum rồi xuất canonical NNNN-NNNX.",
        [
            NormalizerSample("ISSN 2049 3630", "2049-3630"),
            NormalizerSample("ISSN-L: 20493630", "2049-3630"),
            NormalizerSample("2049-3631", None),
        ],
    ),
    "iso2108_normalize_isbn13": NormalizerContract(
        "TRY_PARSE ISBN-10, ISBN-13, ISBN label hoặc urn:isbn representation, validate checksum và xuất canonical 13-digit ISBN-13.",
        [
            NormalizerSample("0-306-40615-2", "9780306406157"),
            NormalizerSample("978-0-306-40615-7", "9780306406157"),
            NormalizerSample("urn:isbn:0-306-40615-2", "9780306406157"),
            NormalizerSample("9780306406158", None),
        ],
    ),
    "w3c_did_normalize": NormalizerContract(
        "TRY_PARSE bare hoặc angle-bracket generic DID, lowercase did scheme/method nhưng giữ method-specific identifier semantics; không áp dụng method-specific rewrite rules.",
        [
            NormalizerSample("DID:WEB:example.com:user:123", "did:web:example.com:user:123"),
            NormalizerSample("<did:WEB:example.com:user:123>", "did:web:example.com:user:123"),
            NormalizerSample("did:web:", None),
        ],
    ),
    "rfc9562_normalize_uuid": NormalizerContract(
        "TRY_PARSE UUID/GUID canonical, compact 32-hex, braces, UUID: hoặc urn:uuid: representation rồi xuất lowercase canonical 8-4-4-4-12 text.",
        [
            NormalizerSample("550E8400-E29B-41D4-A716-446655440000", "550e8400-e29b-41d4-a716-446655440000"),
            NormalizerSample("{550E8400-E29B-41D4-A716-446655440000}", "550e8400-e29b-41d4-a716-446655440000"),
            NormalizerSample("urn:uuid:550e8400e29b41d4a716446655440000", "550e8400-e29b-41d4-a716-446655440000"),
            NormalizerSample("not-a-uuid", None),
        ],
    ),
    "rfc8141_normalize_urn": NormalizerContract(
        "TRY_PARSE bare hoặc angle-bracket generic URN, lowercase urn/NID và uppercase percent-escape hex; không áp dụng namespace-specific equivalence.",
        [
            NormalizerSample("URN:EXAMPLE:a123%2cz456", "urn:example:a123%2Cz456"),
            NormalizerSample("<urn:example:a123%2cz456>", "urn:example:a123%2Cz456"),
            NormalizerSample("urn::abc", None),
        ],
    ),
}


__all__ = [
    "NORMALIZER_CONTRACTS",
    "NormalizerContract",
    "NormalizerSample",
    "SampleInput",
    "SampleOutput",
]
