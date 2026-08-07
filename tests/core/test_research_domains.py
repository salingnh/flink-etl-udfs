from flink_etl_udfs.core.common import (
    canonicalize_json_value,
    flatten_json_value,
    normalize_decimal_value,
    normalize_e164_value,
    normalize_iso_datetime_value,
    quality_number_in_range_value,
)
from flink_etl_udfs.core.finance import (
    normalize_bic_value,
    normalize_iban_value,
    normalize_iso20022_message_type_value,
)
from flink_etl_udfs.core.healthcare import (
    normalize_dicom_uid_value,
    normalize_fhir_reference_value,
    normalize_hl7_message_type_value,
)
from flink_etl_udfs.core.industrial import normalize_obis_code_value, normalize_opcua_node_id_value
from flink_etl_udfs.core.insurance import (
    normalize_acord_version_value,
    normalize_policy_number_value,
)
from flink_etl_udfs.core.scientific import (
    normalize_cf_standard_name_value,
    normalize_chromosome_value,
    normalize_dna_sequence_value,
    normalize_fits_keyword_value,
    normalize_vcf_genotype_value,
)
from flink_etl_udfs.core.security_standards import (
    normalize_attack_technique_id_value,
    normalize_stix_id_value,
)
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
    build_entity_blocking_key_value,
    classify_vn_identity_id_value,
    normalize_academic_year_value,
    normalize_vn_citizen_id_value,
    normalize_vn_name_value,
    normalize_vn_phone_value,
    normalize_vn_tax_id_value,
    vietnamese_name_search_key_value,
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


def test_p1_vietnam() -> None:
    assert normalize_vn_citizen_id_value("034 190 006 609") == "034190006609"
    assert classify_vn_identity_id_value("034190006609") == "cccd_12"
    assert normalize_vn_tax_id_value("0101234567001") == "0101234567-001"
    assert normalize_vn_phone_value("0983 132 288") == "+84983132288"
    assert normalize_vn_name_value("  Nguyễn   Thị Ngân ") == "Nguyễn Thị Ngân"
    assert vietnamese_name_search_key_value("Đặng Thị Hồng") == "dang thi hong"
    assert normalize_academic_year_value("2025/26") == "2025-2026"
    assert build_entity_blocking_key_value("Nguyễn Văn A", "0912345678", "USER@EXAMPLE.COM") == "n=nguyen van a|p=+84912345678|e=user@example.com"


def test_p2_cti_healthcare_finance() -> None:
    assert normalize_stix_id_value("indicator--550e8400-e29b-41d4-a716-446655440000") is not None
    assert normalize_attack_technique_id_value("t1059.001") == "T1059.001"
    assert normalize_fhir_reference_value("Patient/patient-001") == "Patient/patient-001"
    assert normalize_hl7_message_type_value("adt^a01") == "ADT^A01"
    assert normalize_dicom_uid_value("1.2.840.10008.1.2.1") == "1.2.840.10008.1.2.1"
    assert normalize_iban_value("GB82 WEST 1234 5698 7654 32") == "GB82WEST12345698765432"
    assert normalize_bic_value("deut de ff") == "DEUTDEFF"
    assert normalize_iso20022_message_type_value("PACS.008.001.08") == "pacs.008.001.08"


def test_p2_supply_iot_geo() -> None:
    assert normalize_gtin_value("4006381333931") == "4006381333931"
    sscc = _with_gs1_check_digit("12345678901234567")
    assert normalize_sscc_value(sscc) == sscc
    assert normalize_epcis_event_type_value("object_event") == "ObjectEvent"
    assert normalize_opcua_node_id_value("ns=2;s=Temperature") == "ns=2;s=Temperature"
    assert normalize_obis_code_value("1-0:1.8.0*255") == "1-0:1.8.0*255"
    assert normalize_epsg_code_value("epsg:4326") == "EPSG:4326"
    assert normalize_latitude_value("21.0278") == 21.0278
    assert normalize_longitude_value("105.8342") == 105.8342


def test_p3_scientific_and_insurance() -> None:
    assert normalize_chromosome_value("chrM") == "MT"
    assert normalize_dna_sequence_value("acgt n") == "ACGTN"
    assert normalize_vcf_genotype_value("0/1") == "0/1"
    assert normalize_cf_standard_name_value("Air Temperature") == "air_temperature"
    assert normalize_fits_keyword_value("date-obs") == "DATE-OBS"
    assert normalize_acord_version_value("ACORD v2.0") == "2.0"
    assert normalize_policy_number_value(" pl-2026 / 001 ") == "PL-2026/001"
