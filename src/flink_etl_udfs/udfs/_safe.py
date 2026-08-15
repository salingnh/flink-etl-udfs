"""Shared internal TRY_CAST boundary for public PyFlink scalar UDFs.

Public UDFs intentionally do not declare ``input_types``. Flink therefore passes
runtime scalar values through to Python, where each argument is converted to the
logical type expected by the transform. Failed conversions and malformed row data
produce SQL NULL. Infrastructure/runtime failures such as network outages remain
visible and are not swallowed.
"""

from __future__ import annotations

import json
import math
from datetime import date, datetime, time
from decimal import Decimal, InvalidOperation
from functools import wraps
from typing import Callable, Dict

from pyflink.table.udf import udf

_DATA_ERRORS = (
    ArithmeticError,
    AttributeError,
    LookupError,
    TypeError,
    UnicodeError,
    ValueError,
)


def _cast_string(value):
    if value is None:
        return None
    if isinstance(value, str):
        return value
    if isinstance(value, bytes):
        return value.decode("utf-8")
    if isinstance(value, (datetime, date, time)):
        return value.isoformat()
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"), default=str)
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _cast_boolean(value):
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float, Decimal)) and value in (0, 1):
        return bool(value)
    text = _cast_string(value)
    if text is None:
        return None
    normalized = text.strip().casefold()
    if normalized in {"true", "t", "1"}:
        return True
    if normalized in {"false", "f", "0"}:
        return False
    raise ValueError("cannot cast value to BOOLEAN")


def _cast_bigint(value):
    if value is None:
        return None
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, Decimal):
        if value != value.to_integral_value():
            raise ValueError("fractional DECIMAL cannot be cast to BIGINT")
        return int(value)
    if isinstance(value, float):
        if not math.isfinite(value) or not value.is_integer():
            raise ValueError("non-integral DOUBLE cannot be cast to BIGINT")
        return int(value)
    text = _cast_string(value)
    if text is None:
        return None
    return int(text.strip())


def _cast_double(value):
    if value is None:
        return None
    result = float(value)
    if not math.isfinite(result):
        raise ValueError("non-finite value cannot be cast to DOUBLE")
    return result


def _cast_decimal(value):
    if value is None:
        return None
    try:
        result = value if isinstance(value, Decimal) else Decimal(str(value).strip())
    except InvalidOperation as exc:
        raise ValueError("cannot cast value to DECIMAL") from exc
    if not result.is_finite():
        raise ValueError("non-finite value cannot be cast to DECIMAL")
    return result


def _cast_date(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = _cast_string(value)
    if text is None:
        return None
    return date.fromisoformat(text.strip())


def _cast_timestamp(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, time.min)
    text = _cast_string(value)
    if text is None:
        return None
    return datetime.fromisoformat(text.strip().replace("Z", "+00:00"))


_CASTERS: Dict[str, Callable] = {
    "STRING": _cast_string,
    "BOOLEAN": _cast_boolean,
    "BIGINT": _cast_bigint,
    "DOUBLE": _cast_double,
    "DECIMAL": _cast_decimal,
    "DATE": _cast_date,
    "TIMESTAMP": _cast_timestamp,
}


def try_cast_value(value, target_type: str):
    """Convert one runtime value to a transform input type or raise ValueError."""
    caster = _CASTERS.get(target_type.upper())
    if caster is None:
        raise ValueError(f"unsupported internal cast type: {target_type}")
    return caster(value)


def try_null(function, cast_types):
    """Cast arguments internally, then execute the original transform; failures -> NULL."""

    @wraps(function)
    def wrapped(*args, **kwargs):
        try:
            if kwargs or len(args) != len(cast_types):
                raise TypeError("unexpected UDF argument shape")
            casted = [
                try_cast_value(value, target_type)
                for value, target_type in zip(args, cast_types)
            ]
            return function(*casted)
        except _DATA_ERRORS:
            return None

    return wrapped


def try_udf(function, *, cast_types, result_type, deterministic):
    """Create a UDF accepting arbitrary SQL scalar input types and casting internally.

    ``input_types`` is deliberately omitted from :func:`pyflink.table.udf.udf` so
    Flink does not force the call arguments to a fixed logical type before Python
    receives them. The expected transform types are instead declared in
    ``cast_types`` and converted inside ``try_null``.
    """
    return udf(
        try_null(function, cast_types),
        result_type=result_type,
        deterministic=deterministic,
    )


__all__ = ["try_cast_value", "try_null", "try_udf"]
