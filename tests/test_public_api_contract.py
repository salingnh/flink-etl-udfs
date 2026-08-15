"""Contract tests for operation categories and internal TRY_CAST behavior."""

from __future__ import annotations

import importlib.util
import sys
import types
from datetime import date
from pathlib import Path

import pytest

from flink_etl_udfs.public_api import PUBLIC_FUNCTIONS

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
ALLOWED_CATEGORIES = {
    "conversion",
    "validation",
    "classification",
    "generation",
    "masking",
    "fingerprint",
    "extraction",
    "enrichment",
}


def test_categories_are_operation_based_and_every_function_is_try_cast() -> None:
    assert len(PUBLIC_FUNCTIONS) == 66
    assert {spec["category"] for spec in PUBLIC_FUNCTIONS.values()} <= ALLOWED_CATEGORIES
    assert all(spec["error_policy"] == "try_cast" for spec in PUBLIC_FUNCTIONS.values())

    forbidden_categories = {
        "finance",
        "health",
        "security",
        "vietnam",
        "osint",
        "iso",
        "rfc",
        "w3c",
        "gs1",
    }
    assert not ({spec["category"] for spec in PUBLIC_FUNCTIONS.values()} & forbidden_categories)


def test_every_public_entrypoint_module_uses_shared_try_boundary() -> None:
    modules = {spec["entrypoint"].rsplit(".", 1)[0] for spec in PUBLIC_FUNCTIONS.values()}
    for module in modules:
        relative = Path(*module.split(".")).with_suffix(".py")
        source = (SRC / relative).read_text(encoding="utf-8")
        assert "try_udf" in source, f"{module} does not use the shared TRY UDF boundary"
        assert "input_types=" not in source, (
            f"{module} fixes PyFlink input_types; arbitrary SQL values would be cast before Python"
        )


def _load_safe_module(monkeypatch: pytest.MonkeyPatch):
    pyflink = types.ModuleType("pyflink")
    table = types.ModuleType("pyflink.table")
    udf_module = types.ModuleType("pyflink.table.udf")
    udf_module.udf = lambda function, **_: function
    table.udf = udf_module
    pyflink.table = table
    monkeypatch.setitem(sys.modules, "pyflink", pyflink)
    monkeypatch.setitem(sys.modules, "pyflink.table", table)
    monkeypatch.setitem(sys.modules, "pyflink.table.udf", udf_module)

    path = SRC / "flink_etl_udfs" / "udfs" / "_safe.py"
    spec = importlib.util.spec_from_file_location("_safe_contract_test", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_internal_try_cast_converts_arbitrary_runtime_values(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_safe_module(monkeypatch)

    assert module.try_cast_value(123, "STRING") == "123"
    assert module.try_cast_value(True, "STRING") == "true"
    assert module.try_cast_value(date(2026, 8, 15), "STRING") == "2026-08-15"
    assert module.try_cast_value(b"abc", "STRING") == "abc"
    assert module.try_cast_value("42", "BIGINT") == 42
    assert module.try_cast_value("true", "BOOLEAN") is True


def test_try_boundary_casts_before_running_existing_logic(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_safe_module(monkeypatch)

    def prefix(value: str) -> str:
        return "ID-" + value

    wrapped = module.try_null(prefix, ["STRING"])
    assert wrapped(12345) == "ID-12345"
    assert wrapped(date(2026, 8, 15)) == "ID-2026-08-15"


def test_cast_or_row_data_failure_returns_null(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_safe_module(monkeypatch)

    def identity(value):
        return value

    assert module.try_null(identity, ["BIGINT"])("not-an-int") is None

    def bad_value(_: str) -> str:
        raise ValueError("malformed row value")

    assert module.try_null(bad_value, ["STRING"])("x") is None


def test_try_boundary_does_not_hide_infrastructure_outages(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_safe_module(monkeypatch)

    def outage(_: str) -> str:
        raise OSError("service unavailable")

    with pytest.raises(OSError, match="service unavailable"):
        module.try_null(outage, ["STRING"])("x")
