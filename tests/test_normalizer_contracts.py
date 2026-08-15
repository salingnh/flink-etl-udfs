from __future__ import annotations

from flink_etl_udfs.core import common
from flink_etl_udfs.normalizer_contracts import NORMALIZER_CONTRACTS


NORMALIZER_IMPLEMENTATIONS = {
    "iso8601_normalize_date": common.normalize_date_value,
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
