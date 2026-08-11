from flink_etl_udfs.core.common import (
    canonicalize_json_value,
    flatten_json_value,
    latin_name_search_key_value,
    normalize_address_text_value,
    normalize_decimal_value,
    normalize_e164_value,
    normalize_identifier_code_value,
    normalize_iso_datetime_value,
    normalize_person_name_value,
    quality_number_in_range_value,
)
from flink_etl_udfs.core.finance import (
    normalize_bic_value,
    normalize_iban_value,
    normalize_iso20022_message_type_value,
    normalize_lei_value,
)
from flink_etl_udfs.core.healthcare import (
    normalize_dicom_uid_value,
    normalize_fhir_reference_value,
    normalize_hl7_message_type_value,
)
from flink_etl_udfs.core.industrial import normalize_obis_code_value, normalize_opcua_node_id_value
from flink_etl_udfs.core.supply_chain import (
    normalize_epcis_event_type_value,
    normalize_gtin_value,
    normalize_sscc_value,
)
from flink_etl_udfs.core.transport_geo import (
    normalize_epsg_code_value,
    normalize_latitude_value,
    normalize_longitude_value,
)
from flink_etl_udfs.core.vietnam import (
    classify_vn_identity_id_value,
    classify_vn_tax_id_structure_value,
    normalize_vn_citizen_id_value,
    normalize_vn_mobile_phone_value,
    normalize_vn_tax_id_value,
)


def _with_gs1_check_digit(body: str) -> str:
    total = sum(int(ch) * (3 if i % 2 else 1) for i, ch in enumerate(reversed(body), start=1))
    return body + str((10 - total % 10) % 10)


def test_p0_common() -> None:
    assert normalize_iso_datetime_value("2026-08-07T09:00:00+07:00") == "2026-08-07T02:00:00.000000Z"
    assert normalize_decimal_value("00123.4500") == "123.45"
    assert normalize_e164_value("0912 345 678", "+84") == "+84912345678"
    assert canonicalize_json_value('{"b":2,"a":1}') == '{"a":1,"b":2}'
    assert flatten_json_value('{"a":{"b":1}}') == '{"a.b":1}'
    assert quality_number_in_range_value("10.5", "10", "11") is True


def test_generic_identity_and_address_helpers() -> None:
    assert normalize_person_name_value("  Nguyễn   Văn   An  ") == "Nguyễn Văn An"
    assert latin_name_search_key_value("Đặng Thị Hồng") == "dang thi hong"
    assert normalize_identifier_code_value(" hs- 2026 / 001 ") == "HS-2026/001"
    assert normalize_address_text_value("12 Nguyễn Trãi,   P. Bến Thành") == "12 Nguyễn Trãi, P. Bến Thành"


def test_vietnam_specific_identifiers() -> None:
    assert normalize_vn_citizen_id_value("034 190 006 609") == "034190006609"
    assert classify_vn_identity_id_value("034190006609") == "cccd_12"
    assert normalize_vn_tax_id_value("0101234567001") == "0101234567-001"
    assert classify_vn_tax_id_structure_value("0101234567") == "base_10"
    assert classify_vn_tax_id_structure_value("0101234567-001") == "extended_13"


def test_vietnam_mobile_phone_normalization() -> None:
    # Current 10-digit national and international representations.
    assert normalize_vn_mobile_phone_value("0912 345 678") == "0912345678"
    assert normalize_vn_mobile_phone_value("+84 912 345 678") == "0912345678"
    assert normalize_vn_mobile_phone_value("0084 912 345 678") == "0912345678"

    # 2018 network-code migrations: Viettel, VinaPhone, MobiFone, Vietnamobile, Gmobile.
    assert normalize_vn_mobile_phone_value("0169 123 4567") == "0391234567"
    assert normalize_vn_mobile_phone_value("0124 123 4567") == "0841234567"
    assert normalize_vn_mobile_phone_value("0120 123 4567") == "0701234567"
    assert normalize_vn_mobile_phone_value("0188 123 4567") == "0581234567"
    assert normalize_vn_mobile_phone_value("0199 123 4567") == "0591234567"
    assert normalize_vn_mobile_phone_value("+84 169 123 4567") == "0391234567"

    # Do not infer unsupported/ambiguous fixed-line or malformed numbers.
    assert normalize_vn_mobile_phone_value("024 3825 0000") is None
    assert normalize_vn_mobile_phone_value("0111 123 4567") is None
    assert normalize_vn_mobile_phone_value("123456789") is None


def test_healthcare_and_finance_standards() -> None:
    assert normalize_fhir_reference_value("Patient/patient-001") == "Patient/patient-001"
    assert normalize_hl7_message_type_value("adt^a01") == "ADT^A01"
    assert normalize_dicom_uid_value("1.2.840.10008.1.2.1") == "1.2.840.10008.1.2.1"
    assert normalize_iban_value("GB82 WEST 1234 5698 7654 32") == "GB82WEST12345698765432"
    assert normalize_bic_value("deut de ff") == "DEUTDEFF"
    assert normalize_iso20022_message_type_value("PACS.008.001.08") == "pacs.008.001.08"
    assert normalize_lei_value("5493001KJTIIGC8Y1R12") == "5493001KJTIIGC8Y1R12"


def test_supply_industrial_and_geo_standards() -> None:
    assert normalize_gtin_value("4006381333931") == "4006381333931"
    sscc = _with_gs1_check_digit("12345678901234567")
    assert normalize_sscc_value(sscc) == sscc
    assert normalize_epcis_event_type_value("object_event") == "ObjectEvent"
    assert normalize_opcua_node_id_value("ns=2;s=Temperature") == "ns=2;s=Temperature"
    assert normalize_obis_code_value("1-0:1.8.0*255") == "1-0:1.8.0*255"
    assert normalize_epsg_code_value("epsg:4326") == "EPSG:4326"
    assert normalize_latitude_value("21.0278") == 21.0278
    assert normalize_longitude_value("105.8342") == 105.8342
