from flink_etl_udfs.core.privacy import (
    mask_email_value,
    mask_text_value,
    sha256_fingerprint_value,
)


def test_sha256_preserves_null() -> None:
    assert sha256_fingerprint_value(None) is None


def test_sha256_is_deterministic() -> None:
    assert sha256_fingerprint_value("abc") == (
        "ba7816bf8f01cfea414140de5dae2223"
        "b00361a396177a9cb410ff61f20015ad"
    )


def test_mask_text() -> None:
    assert mask_text_value(None) is None
    assert mask_text_value("") == ""
    assert mask_text_value("a") == "*"
    assert mask_text_value("ab") == "**"
    assert mask_text_value("abcdef") == "a****f"


def test_mask_email() -> None:
    assert mask_email_value("alice@example.com") == "a***e@example.com"
    assert mask_email_value("x@example.com") == "*@example.com"
