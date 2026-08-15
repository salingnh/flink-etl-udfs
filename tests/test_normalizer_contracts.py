from __future__ import annotations

from flink_etl_udfs.core import common
from flink_etl_udfs.normalizer_contracts import NORMALIZER_CONTRACTS


NORMALIZER_IMPLEMENTATIONS = {
    "iso8601_normalize_date": common.normalize_date_value,
    "iso8601_normalize_datetime_utc": common.normalize_iso_datetime_value,
    "etl_normalize_decimal": common.normalize_decimal_value,
    "iso4217_normalize_currency_code": common.normalize_currency_code_value,
    "itu_e164_normalize_phone": common.normalize_e164_value,
    "etl_normalize_null_token": common.normalize_null_token_value,
    "etl_normalize_person_name": common.normalize_person_name_value,
    "etl_normalize_identifier_code": common.normalize_identifier_code_value,
    "etl_normalize_address_text": common.normalize_address_text_value,
}


def _as_args(value):
    return value if isinstance(value, tuple) else (value,)


def test_normalizer_contract_samples() -> None:
    assert set(NORMALIZER_CONTRACTS) <= set(NORMALIZER_IMPLEMENTATIONS)
    for func_key, contract in NORMALIZER_CONTRACTS.items():
        implementation = NORMALIZER_IMPLEMENTATIONS[func_key]
        assert contract.description.strip()
        assert len(contract.samples) >= 2
        for sample in contract.samples:
            assert implementation(*_as_args(sample.input)) == sample.output, (
                func_key,
                sample,
            )
