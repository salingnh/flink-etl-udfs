from flink_etl_udfs.core.osint_evidence import (
    build_observation_id_value,
    content_sha256_value,
    normalize_confidence_value,
    normalize_observed_at_utc_value,
    normalize_verification_status_value,
)


def test_content_sha256_is_deterministic() -> None:
    assert content_sha256_value("evidence") == content_sha256_value("evidence")


def test_observation_id_requires_all_components() -> None:
    value = build_observation_id_value(
        "https://example.com/u/a", "account:example:a", "2026-08-07T00:00:00Z"
    )
    assert value is not None and len(value) == 64
    assert build_observation_id_value(None, "key", "time") is None


def test_confidence_accepts_only_unit_interval() -> None:
    assert normalize_confidence_value("0.72") == 0.72
    assert normalize_confidence_value("1.1") is None
    assert normalize_confidence_value("NaN") is None


def test_verification_status_mapping() -> None:
    assert normalize_verification_status_value("Reviewed") == "analyst_reviewed"
    assert normalize_verification_status_value("something-new") is None


def test_observed_at_requires_timezone_and_normalizes_utc() -> None:
    assert normalize_observed_at_utc_value("2026-08-07T07:30:00+07:00") == (
        "2026-08-07T00:30:00Z"
    )
    assert normalize_observed_at_utc_value("2026-08-07T07:30:00") is None
