"""Executable sample contracts shared by unit tests and Elasticsearch metadata.

Each normalizer is added here only after its implementation supports the documented
representations. Tests execute these exact cases; the metadata exporter renders the
same cases into the public description so runtime and documentation cannot drift.
"""

from __future__ import annotations

from typing import Dict, List, NamedTuple, Optional, Union

Scalar = Union[str, int, float, bool, None]
SampleInput = Union[Scalar, tuple[Scalar, ...]]
SampleOutput = Union[str, int, float, bool, None]


class NormalizerSample(NamedTuple):
    input: SampleInput
    output: SampleOutput


class NormalizerContract(NamedTuple):
    description: str
    samples: List[NormalizerSample]


NORMALIZER_CONTRACTS: Dict[str, NormalizerContract] = {
    "iso8601_normalize_date": NormalizerContract(
        description=(
            "TRY_PARSE các representation ngày phổ biến có thể xác định an toàn và "
            "xuất một giá trị canonical YYYY-MM-DD; input không hợp lệ hoặc mơ hồ "
            "giữa nhiều date order trả NULL."
        ),
        samples=[
            NormalizerSample("2026-08-15", "2026-08-15"),
            NormalizerSample("15/08/2026", "2026-08-15"),
            NormalizerSample("20260815", "2026-08-15"),
            NormalizerSample("01/02/2026", None),
            NormalizerSample("31/02/2026", None),
        ],
    ),
}


__all__ = [
    "NORMALIZER_CONTRACTS",
    "NormalizerContract",
    "NormalizerSample",
    "SampleInput",
    "SampleOutput",
]
