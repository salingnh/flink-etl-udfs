"""Minimal PyFlink UDFs for runtime/serialization benchmarking.

These functions are intentionally kept outside the curated public ETL catalog.
They are useful for measuring the baseline cost of crossing the JVM/Python
boundary without adding transformation logic.
"""

from __future__ import annotations

from pyflink.table import DataTypes
from pyflink.table.udf import udf


@udf(
    result_type=DataTypes.STRING(),
    deterministic=True,
)
def python_noop(value):
    """Return the input unchanged to benchmark JVM <-> Python UDF overhead."""
    return value


__all__ = ["python_noop"]
