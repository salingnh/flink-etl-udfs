"""Contract tests for operation categories and TRY-style public UDF behavior."""

from __future__ import annotations

import importlib.util
import sys
import types
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

    # Standards/domains belong in `standard` or the function name, never category.
    forbidden_category_fragments = {
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
    assert not (
        {spec["category"] for spec in PUBLIC_FUNCTIONS.values()}
        & forbidden_category_fragments
    )


def test_every_public_entrypoint_module_uses_shared_try_boundary() -> None:
    modules = {spec["entrypoint"].rsplit(".", 1)[0] for spec in PUBLIC_FUNCTIONS.values()}
    for module in modules:
        relative = Path(*module.split(".")).with_suffix(".py")
        source = (SRC / relative).read_text(encoding="utf-8")
        assert "try_udf" in source, f"{module} does not use the shared TRY UDF boundary"


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


def test_try_boundary_returns_null_for_row_data_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_safe_module(monkeypatch)

    def bad_value(_: object) -> str:
        raise ValueError("malformed row value")

    def bad_type(_: object) -> str:
        raise AttributeError("wrong runtime value shape")

    assert module.try_null(bad_value)("x") is None
    assert module.try_null(bad_type)(123) is None


def test_try_boundary_does_not_hide_infrastructure_outages(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_safe_module(monkeypatch)

    def outage(_: object) -> str:
        raise OSError("service unavailable")

    with pytest.raises(OSError, match="service unavailable"):
        module.try_null(outage)("x")
