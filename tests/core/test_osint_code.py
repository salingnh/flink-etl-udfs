from flink_etl_udfs.core.osint_code import (
    classify_git_object_hash_value,
    normalize_git_object_id_value,
    normalize_repository_url_value,
)


def test_normalize_repository_url() -> None:
    assert normalize_repository_url_value(
        "https://github.com/salingnh/flink-etl-udfs.git?utm_source=test"
    ) == "https://github.com/salingnh/flink-etl-udfs"


def test_full_git_object_ids_only() -> None:
    sha1 = "A" * 40
    assert normalize_git_object_id_value(sha1) == "a" * 40
    assert classify_git_object_hash_value(sha1) == "sha1"
    assert normalize_git_object_id_value("abc1234") is None
