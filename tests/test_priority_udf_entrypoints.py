"""Static contract tests for SQL-loaded Python UDF entrypoints."""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "flink_etl_udfs"


def _module_tree(relative_path: str) -> ast.Module:
    return ast.parse((SRC / relative_path).read_text(encoding="utf-8"))


def test_profile_extract_entrypoint_is_sync_try_udf_object() -> None:
    tree = _module_tree("udfs/enrichment.py")

    assert not any(isinstance(node, ast.AsyncFunctionDef) for node in ast.walk(tree))

    assignment = next(
        node
        for node in tree.body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "extract_profile_url" for target in node.targets)
    )
    assert isinstance(assignment.value, ast.Call)
    assert isinstance(assignment.value.func, ast.Name)
    assert assignment.value.func.id == "try_udf"
    assert assignment.value.args
    assert isinstance(assignment.value.args[0], ast.Name)
    assert assignment.value.args[0].id == "extract_profile_url_sync"


def test_vietnam_phone_entrypoint_is_self_contained_scalar_udf_object() -> None:
    tree = _module_tree("udfs/vietnam.py")

    imported_modules = {
        node.module
        for node in tree.body
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }
    assert "flink_etl_udfs.core.vietnam" not in imported_modules
    assert "flink_etl_udfs.core" not in imported_modules
    assert "flink_etl_udfs.udfs._safe" in imported_modules

    helper = next(
        node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "_string_udf"
    )
    helper_calls = [node for node in ast.walk(helper) if isinstance(node, ast.Call)]
    assert any(isinstance(call.func, ast.Name) and call.func.id == "try_udf" for call in helper_calls)

    assignment = next(
        node
        for node in tree.body
        if isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Name) and target.id == "normalize_vn_mobile_phone"
            for target in node.targets
        )
    )
    assert isinstance(assignment.value, ast.Call)
    assert isinstance(assignment.value.func, ast.Name)
    assert assignment.value.func.id == "_string_udf"
    assert assignment.value.args
    argument = assignment.value.args[0]
    assert isinstance(argument, ast.Name)
    assert argument.id == "_normalize_vn_mobile_phone"
