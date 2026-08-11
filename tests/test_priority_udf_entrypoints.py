"""Static contract tests for SQL-loaded Python UDF entrypoints."""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "flink_etl_udfs"


def _module_tree(relative_path: str) -> ast.Module:
    return ast.parse((SRC / relative_path).read_text(encoding="utf-8"))


def test_profile_extract_entrypoint_is_direct_sync_udf_object() -> None:
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
    assert assignment.value.func.id == "udf"
    assert assignment.value.args
    assert isinstance(assignment.value.args[0], ast.Name)
    assert assignment.value.args[0].id == "extract_profile_url_sync"


def test_vietnam_phone_entrypoint_remains_direct_scalar_udf_object() -> None:
    tree = _module_tree("udfs/research_domains.py")

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
    assert assignment.value.func.id == "_s"
    assert assignment.value.args
    argument = assignment.value.args[0]
    assert isinstance(argument, ast.Attribute)
    assert argument.attr == "normalize_vn_mobile_phone_value"
