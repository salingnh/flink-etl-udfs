"""Apply executable normalizer contracts before exporting Elasticsearch metadata."""

from __future__ import annotations

import export_elastic_metadata as exporter

from flink_etl_udfs.normalizer_contracts import NORMALIZER_CONTRACTS

STANDARD_DESCRIPTION_OVERRIDES = {
    "ISO 8601": (
        "ISO 8601 là tiêu chuẩn quốc tế cho biểu diễn ngày và thời gian. Trong các "
        "normalizer của thư viện, ISO 8601 xác định canonical output; input có thể ở "
        "representation khác nếu TRY_PARSE được deterministic và không mơ hồ."
    ),
}


def apply_normalizer_contracts() -> None:
    """Use executable normalizer samples as the metadata descriptions/examples."""
    for func_key, contract in NORMALIZER_CONTRACTS.items():
        if func_key not in exporter.FUNCTION_DESCRIPTIONS or func_key not in exporter.EXAMPLES:
            raise RuntimeError(f"normalizer is not present in metadata catalog: {func_key}")
        exporter.FUNCTION_DESCRIPTIONS[func_key] = contract.description
        exporter.EXAMPLES[func_key] = [
            (sample.input, sample.output) for sample in contract.samples
        ]

    exporter.STANDARD_DESCRIPTIONS.update(STANDARD_DESCRIPTION_OVERRIDES)


def main() -> None:
    apply_normalizer_contracts()
    exporter.main()


if __name__ == "__main__":
    main()
