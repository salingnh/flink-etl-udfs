from flink_etl_udfs.core.osint_infrastructure import (
    normalize_asn_value,
    normalize_dns_record_type_value,
    normalize_mime_type_value,
)


def test_normalize_asn() -> None:
    assert normalize_asn_value(" as13335 ") == "AS13335"
    assert normalize_asn_value("not-asn") is None


def test_dns_record_type_is_controlled() -> None:
    assert normalize_dns_record_type_value("aaaa") == "AAAA"
    assert normalize_dns_record_type_value("BOGUS") is None


def test_normalize_mime_type_drops_parameters() -> None:
    assert normalize_mime_type_value("Text/HTML; charset=UTF-8") == "text/html"
    assert normalize_mime_type_value("invalid") is None
