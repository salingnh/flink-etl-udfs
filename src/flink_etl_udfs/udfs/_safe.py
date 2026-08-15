"""Shared TRY-like error boundary for public PyFlink scalar UDFs.

The SQL-facing contract is fail-soft for row-data errors: malformed input should
produce SQL NULL instead of failing the Flink task. Infrastructure/runtime errors
such as network outages remain visible and are not swallowed here.
"""

from __future__ import annotations

from functools import wraps

from pyflink.table.udf import udf

# Expected exceptions caused by malformed row values or conversion/parsing logic.
# Deliberately excludes OSError/TimeoutError so external-service outages do not
# silently become missing business data.
_DATA_ERRORS = (
    ArithmeticError,
    AttributeError,
    LookupError,
    TypeError,
    UnicodeError,
    ValueError,
)


def try_null(function):
    """Wrap a scalar transform with SQL TRY semantics: data error -> ``None``."""

    @wraps(function)
    def wrapped(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except _DATA_ERRORS:
            return None

    return wrapped


def try_udf(function, *, input_types, result_type, deterministic):
    """Create a PyFlink UDF whose row-data failures return SQL NULL."""
    return udf(
        try_null(function),
        input_types=input_types,
        result_type=result_type,
        deterministic=deterministic,
    )


__all__ = ["try_null", "try_udf"]
