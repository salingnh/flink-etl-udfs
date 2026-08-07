from flink_etl_udfs.core.osint_identity import (
    classify_account_identifier_value,
    normalize_name_search_key_value,
    normalize_platform_value,
    normalize_username_value,
)


def test_normalize_username_preserves_case() -> None:
    assert normalize_username_value("  @@User.Name  ") == "User.Name"


def test_normalize_platform() -> None:
    assert normalize_platform_value(" WWW.Tumblr.COM. ") == "tumblr.com"


def test_name_search_key_is_not_canonical_identity() -> None:
    assert normalize_name_search_key_value(" Nguyễn  Văn-A ") == "nguyen van a"


def test_classify_account_identifier() -> None:
    assert classify_account_identifier_value("person@example.com") == "email"
    assert classify_account_identifier_value("+84 912 345 678") == "phone"
    assert classify_account_identifier_value("chambergambit") == "username"
