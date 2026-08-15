from __future__ import annotations

import json
from pathlib import Path

from flink_etl_udfs.normalizer_contracts import NORMALIZER_CONTRACTS

ROOT = Path(__file__).resolve().parents[1]
METADATA_PATH = ROOT / "metadata" / "flink_transform_functions_elastic_v0.7.1.json"


def _format_value(value) -> str:
    if value is None:
        return "NULL"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, tuple):
        return "(" + ", ".join(_format_value(item) for item in value) + ")"
    return json.dumps(value, ensure_ascii=False)


def test_elasticsearch_descriptions_use_exact_normalizer_contract_samples() -> None:
    documents = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    by_key = {document["func_key"]: document for document in documents}

    for func_key, contract in NORMALIZER_CONTRACTS.items():
        description = by_key[func_key]["description"]
        assert contract.description in description
        for sample in contract.samples:
            example = (
                f"- Input: `{_format_value(sample.input)}` → "
                f"Output: `{_format_value(sample.output)}`"
            )
            assert example in description, (func_key, example)
