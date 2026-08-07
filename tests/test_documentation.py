"""Documentation-contract tests for public transforms and registered SQL UDFs."""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "flink_etl_udfs"


def _registered_sql_names() -> set[str]:
    tree = ast.parse((SRC / "registry.py").read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef):
            continue
        if not node.name.startswith("register_") or node.name == "register_all_udfs":
            continue
        for child in ast.walk(node):
            if not isinstance(child, ast.Dict):
                continue
            for key in child.keys:
                if isinstance(key, ast.Constant) and isinstance(key.value, str):
                    names.add(key.value)
    return names


def test_every_public_core_function_has_docstring() -> None:
    missing: list[str] = []
    for path in sorted((SRC / "core").glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in tree.body:
            if not isinstance(node, ast.FunctionDef) or node.name.startswith("_"):
                continue
            if ast.get_docstring(node) is None:
                missing.append(f"{path.name}:{node.name}")
    assert not missing, f"public core functions missing docstrings: {missing}"


def test_function_catalog_mentions_every_registered_sql_udf() -> None:
    catalog_parts = [
        (ROOT / "docs" / "FUNCTION_CATALOG.md").read_text(encoding="utf-8"),
        *(path.read_text(encoding="utf-8") for path in sorted((ROOT / "docs" / "functions").glob("*.md"))),
    ]
    catalog = "\n".join(catalog_parts)
    missing = sorted(name for name in _registered_sql_names() if f"`{name}`" not in catalog)
    assert not missing, f"registered UDFs missing from function catalog: {missing}"
