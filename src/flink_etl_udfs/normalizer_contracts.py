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


NORMALIZER_CONTRACTS: Dict[str, NormalizerContract] = {
    "iso8601_normalize_date": NormalizerContract(
        description=(
            "TRY_PARSE các representation ngày phổ biến có thể xác định an toàn và "
            "xuất một giá trị canonical YYYY-MM-DD; input không hợp lệ hoặc mơ hồ "
            "giữa nhiều date order trả NULL."
        ),
        samples=[
            NormalizerSample("2026-08-15", "2026-08-15"),
            NormalizerSample("15/08/2026", "2026-08-15"),
            NormalizerSample("20260815", "2026-08-15"),
            NormalizerSample("01/02/2026", None),
            NormalizerSample("31/02/2026", None),
        ],
    ),
    "iso8601_normalize_datetime_utc": NormalizerContract(
        description=(
            "TRY_PARSE các timestamp có timezone từ những representation xác định được "
            "an toàn rồi canonicalize về UTC với hậu tố Z; không tự đoán timezone và "
            "không đoán date order mơ hồ."
        ),
        samples=[
            NormalizerSample(
                "2026-08-15T09:00:00+07:00", "2026-08-15T02:00:00.000000Z"
            ),
            NormalizerSample(
                "15/08/2026 09:00:00+07:00", "2026-08-15T02:00:00.000000Z"
            ),
            NormalizerSample(
                "2026/08/15 09:00 +0700", "2026-08-15T02:00:00.000000Z"
            ),
            NormalizerSample("01/02/2026 09:00:00+07:00", None),
            NormalizerSample("2026-08-15 09:00:00", None),
        ],
    ),
    "etl_normalize_decimal": NormalizerContract(
        description=(
            "TRY_PARSE số thập phân từ representation dấu chấm/dấu phẩy có thể xác định "
            "deterministic, loại grouping separator và xuất decimal text canonical; "
            "representation mơ hồ như 1,234 trả NULL thay vì đoán."
        ),
        samples=[
            NormalizerSample("00123.4500", "123.45"),
            NormalizerSample("1.234,50", "1234.5"),
            NormalizerSample("1,234.50", "1234.5"),
            NormalizerSample("1,234", None),
            NormalizerSample("NaN", None),
        ],
    ),
    "iso4217_normalize_currency_code": NormalizerContract(
        description=(
            "Chuẩn hóa mã tiền tệ ISO 4217 alpha-3 hoặc numeric được gán trong reference "
            "data sang alpha-3 canonical; không đoán currency name hoặc symbol mơ hồ."
        ),
        samples=[
            NormalizerSample("vnd", "VND"),
            NormalizerSample("704", "VND"),
            NormalizerSample("ISO 4217: usd", "USD"),
            NormalizerSample("ZZZ", None),
            NormalizerSample("dollar", None),
        ],
    ),
    "itu_e164_normalize_phone": NormalizerContract(
        description=(
            "TRY_PARSE số điện thoại từ các separator phổ biến, prefix +/00/tel: và "
            "default country calling code rồi xuất dạng quốc tế +<digits>; extension, "
            "vanity text hoặc giá trị không xác định an toàn trả NULL."
        ),
        samples=[
            NormalizerSample(("0912 345 678", "+84"), "+84912345678"),
            NormalizerSample(("tel:+84 (912) 345-678", None), "+84912345678"),
            NormalizerSample(("0084 912 345 678", None), "+84912345678"),
            NormalizerSample(("0912FLOWERS", "+84"), None),
            NormalizerSample(("+84 912 345 678;ext=123", None), None),
        ],
    ),
    "etl_normalize_null_token": NormalizerContract(
        description=(
            "Trim input và quy các textual null marker phổ biến về NULL; giá trị text "
            "thực được giữ lại sau khi trim."
        ),
        samples=[
            NormalizerSample(" null ", None),
            NormalizerSample("(NULL)", None),
            NormalizerSample("\\N", None),
            NormalizerSample("  Alice  ", "Alice"),
        ],
    ),
    "etl_normalize_person_name": NormalizerContract(
        description=(
            "Chuẩn hóa tên người theo Unicode NFC và collapse mọi whitespace về một "
            "space, đồng thời giữ nguyên letter case và không đoán thứ tự họ/tên."
        ),
        samples=[
            NormalizerSample("  Nguyễn   Văn   An  ", "Nguyễn Văn An"),
            NormalizerSample("Alice\n\tSmith", "Alice Smith"),
            NormalizerSample(" null ", None),
        ],
    ),
    "etl_normalize_identifier_code": NormalizerContract(
        description=(
            "Chuẩn hóa business identifier generic bằng cách bỏ whitespace, uppercase "
            "và chỉ chấp nhận syntax A-Z, digit, dot, underscore, slash và hyphen."
        ),
        samples=[
            NormalizerSample(" hs- 2026 / 001 ", "HS-2026/001"),
            NormalizerSample("ab.cd_01", "AB.CD_01"),
            NormalizerSample("abc@123", None),
        ],
    ),
    "etl_normalize_address_text": NormalizerContract(
        description=(
            "Chuẩn hóa Unicode/whitespace của địa chỉ text và spacing quanh dấu phẩy, "
            "chấm phẩy; không suy diễn mã hành chính, postal code hay geocode."
        ),
        samples=[
            NormalizerSample(
                "12 Nguyễn Trãi,   P. Bến Thành", "12 Nguyễn Trãi, P. Bến Thành"
            ),
            NormalizerSample("  1 Main St ;  District 1 ", "1 Main St; District 1"),
            NormalizerSample("null", None),
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
