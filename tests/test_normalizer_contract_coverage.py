from flink_etl_udfs.normalizer_contracts import NORMALIZER_CONTRACTS
from flink_etl_udfs.public_api import PUBLIC_FUNCTIONS


def test_every_public_conversion_has_executable_sample_contract() -> None:
    conversion_functions = {
        func_key
        for func_key, spec in PUBLIC_FUNCTIONS.items()
        if spec["category"] == "conversion"
    }
    assert set(NORMALIZER_CONTRACTS) == conversion_functions
