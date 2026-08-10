from flink_etl_udfs.core.osint import build_observation_id_value, normalize_username_value


def test_normalize_username_preserves_case() -> None:
    assert normalize_username_value("  @@User.Name  ") == "User.Name"


def test_observation_id_requires_all_components() -> None:
    value = build_observation_id_value(
        "https://example.com/u/a", "account:example:a", "2026-08-10T00:00:00Z"
    )
    assert value is not None and len(value) == 64
    assert build_observation_id_value(None, "key", "time") is None
