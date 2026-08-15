"""Canonical Elasticsearch metadata exporter for the public Flink ETL UDF catalog.

This is the only supported metadata generation entrypoint. It always applies the
executable normalizer contracts before writing JSON/NDJSON so runtime samples,
descriptions, and generated metadata cannot drift apart.
"""

from __future__ import annotations

import _elastic_metadata_catalog as catalog

from flink_etl_udfs.normalizer_contracts import NORMALIZER_CONTRACTS

ARTIFACT_URI = "s3://fusion-center/transform-library/flink_etl_udfs.zip"

STANDARD_DESCRIPTION_OVERRIDES = {
    "ISO 8601": (
        "ISO 8601 là tiêu chuẩn quốc tế cho biểu diễn ngày và thời gian. Trong các "
        "normalizer của thư viện, ISO 8601 xác định canonical output; input có thể ở "
        "representation khác nếu TRY_PARSE được deterministic và không mơ hồ."
    ),
}


def apply_normalizer_contracts() -> None:
    """Apply executable normalizer contracts to the internal metadata catalog."""
    catalog.ARTIFACT_URI = ARTIFACT_URI

    for func_key, contract in NORMALIZER_CONTRACTS.items():
        if func_key not in catalog.FUNCTION_DESCRIPTIONS or func_key not in catalog.EXAMPLES:
            raise RuntimeError(f"normalizer is not present in metadata catalog: {func_key}")
        catalog.FUNCTION_DESCRIPTIONS[func_key] = contract.description
        catalog.EXAMPLES[func_key] = [
            (sample.input, sample.output) for sample in contract.samples
        ]

    catalog.STANDARD_DESCRIPTIONS.update(STANDARD_DESCRIPTION_OVERRIDES)


def build_documents() -> list[dict]:
    """Build canonical documents without writing files."""
    apply_normalizer_contracts()
    return catalog.build_documents()


def main() -> None:
    apply_normalizer_contracts()
    catalog.main()


if __name__ == "__main__":
    main()
