from flink_etl_udfs.core.osint_security import (
    classify_hash_type_value,
    normalize_cve_value,
    normalize_exposure_status_value,
    normalize_hex_hash_value,
)


def test_normalize_and_classify_hash() -> None:
    digest = "A" * 64
    assert normalize_hex_hash_value(digest) == "a" * 64
    assert classify_hash_type_value(digest) == "sha256"


def test_unknown_hash_length_is_rejected() -> None:
    assert normalize_hex_hash_value("abc123") is None


def test_normalize_cve() -> None:
    assert normalize_cve_value("cve 2024 12345") == "CVE-2024-12345"
    assert normalize_cve_value("CVE-24-1") is None


def test_normalize_exposure_status() -> None:
    assert normalize_exposure_status_value("resolved") == "remediated"
    assert normalize_exposure_status_value("ignored") == "suppressed"
