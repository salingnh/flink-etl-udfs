from flink_etl_udfs.core.osint_compliance import (
    normalize_entity_type_value,
    normalize_lei_value,
    normalize_ownership_percentage_value,
)


def test_normalize_lei_with_known_valid_identifier() -> None:
    assert normalize_lei_value("5493001KJTIIGC8Y1R12") == "5493001KJTIIGC8Y1R12"
    assert normalize_lei_value("5493001KJTIIGC8Y1R13") is None


def test_ownership_percentage() -> None:
    assert normalize_ownership_percentage_value("25.5%") == 25.5
    assert normalize_ownership_percentage_value("101") is None


def test_entity_type_mapping() -> None:
    assert normalize_entity_type_value("Company") == "organization"
    assert normalize_entity_type_value("account") == "online_account"
    assert normalize_entity_type_value("unknown-type") is None
