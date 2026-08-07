from flink_etl_udfs.core.identifiers import digits_only_value, normalize_email_value


def test_normalize_email_only_lowercases_domain() -> None:
    assert normalize_email_value(" User.Name@EXAMPLE.COM ") == "User.Name@example.com"


def test_invalid_email_shape_returns_null() -> None:
    assert normalize_email_value("not-an-email") is None


def test_digits_only() -> None:
    assert digits_only_value("+84 (912) 345-678") == "84912345678"
