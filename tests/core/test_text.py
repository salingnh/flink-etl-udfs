from flink_etl_udfs.core.text import (
    normalize_unicode_nfc_value,
    normalize_whitespace_value,
    null_if_blank_value,
)


def test_normalize_whitespace() -> None:
    assert normalize_whitespace_value("  hello\n\tworld  ") == "hello world"


def test_null_if_blank() -> None:
    assert null_if_blank_value("   ") is None
    assert null_if_blank_value(" a ") == "a"


def test_unicode_nfc() -> None:
    assert normalize_unicode_nfc_value("e\u0301") == "é"
