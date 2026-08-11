"""Dependency-contract tests for Flink deployment packaging."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "flink_etl_udfs"

# Python 3.9 does not expose sys.stdlib_module_names, so keep a conservative
# fallback covering the standard-library imports used by this project.
_FALLBACK_STDLIB = {
    "ast",
    "asyncio",
    "datetime",
    "decimal",
    "hashlib",
    "ipaddress",
    "json",
    "math",
    "os",
    "pathlib",
    "re",
    "sys",
    "typing",
    "unicodedata",
    "urllib",
    "uuid",
}

# Import name -> pip package/file that provides it.
_EXTERNAL_IMPORTS = {
    "pyflink": ("requirements-flink.txt", "apache-flink==2.3.0"),
}


def _import_roots() -> set[str]:
    roots: set[str] = set()
    for path in SRC.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                roots.update(alias.name.split(".", 1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                roots.add(node.module.split(".", 1)[0])
    return roots


def test_all_external_imports_have_a_declared_pip_provider() -> None:
    stdlib = set(getattr(sys, "stdlib_module_names", _FALLBACK_STDLIB)) | _FALLBACK_STDLIB
    internal = {"__future__", "flink_etl_udfs"}
    external = _import_roots() - stdlib - internal
    unknown = sorted(external - set(_EXTERNAL_IMPORTS))
    assert not unknown, (
        "external imports are not mapped to requirements files: "
        f"{unknown}. Add the pip package to requirements and update _EXTERNAL_IMPORTS."
    )


def test_declared_external_import_providers_exist() -> None:
    for import_name, (requirements_file, expected_requirement) in _EXTERNAL_IMPORTS.items():
        path = ROOT / requirements_file
        assert path.exists(), f"{import_name} requires missing {requirements_file}"
        content = path.read_text(encoding="utf-8")
        assert expected_requirement in content, (
            f"{import_name} is imported by source but {expected_requirement!r} "
            f"is missing from {requirements_file}"
        )


def test_worker_requirements_do_not_reinstall_pyflink() -> None:
    content = (ROOT / "requirements.txt").read_text(encoding="utf-8")
    active_lines = [
        line.strip()
        for line in content.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    assert not any(line.startswith("apache-flink") for line in active_lines), (
        "requirements.txt is passed to Flink workers; keep apache-flink in "
        "requirements-flink.txt so the job does not reinstall PyFlink per worker."
    )
