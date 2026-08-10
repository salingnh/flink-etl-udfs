from flink_etl_udfs.core.security import (
    classify_hash_type_value,
    normalize_cve_value,
    normalize_hex_hash_value,
)
from flink_etl_udfs.core.security_standards import (
    normalize_attack_technique_id_value,
    normalize_stix_id_value,
)


def test_normalize_and_classify_hash() -> None:
    digest = "A" * 64
    assert normalize_hex_hash_value(digest) == "a" * 64
    assert classify_hash_type_value(digest) == "sha256"
    assert normalize_hex_hash_value("abc123") is None


def test_normalize_cve() -> None:
    assert normalize_cve_value("cve 2024 12345") == "CVE-2024-12345"
    assert normalize_cve_value("CVE-24-1") is None


def test_cti_identifiers() -> None:
    assert normalize_attack_technique_id_value("t1059.001") == "T1059.001"
    assert normalize_stix_id_value("indicator--550e8400-e29b-41d4-a716-446655440000") is not None
