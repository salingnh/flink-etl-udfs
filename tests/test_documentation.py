"""Documentation and naming-contract tests for the curated SQL-facing UDF API."""

from __future__ import annotations

import ast
from pathlib import Path

from flink_etl_udfs.public_api import PUBLIC_FUNCTIONS

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "flink_etl_udfs"


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


def test_public_api_has_unique_standard_first_metadata() -> None:
    assert PUBLIC_FUNCTIONS
    entrypoints = [metadata["entrypoint"] for metadata in PUBLIC_FUNCTIONS.values()]
    assert len(entrypoints) == len(set(entrypoints)), "public entrypoints must not be duplicated"

    for func_key, metadata in PUBLIC_FUNCTIONS.items():
        assert func_key == func_key.lower()
        assert metadata["name"].strip()
        assert metadata["entrypoint"].startswith("flink_etl_udfs.udfs.")
        standard = metadata["standard"]
        if standard is not None:
            standard_prefix = standard.casefold().split()[0].replace("/", "_").replace("-", "")
            if standard_prefix == "itu_t":
                assert func_key.startswith("itu_")
            elif standard_prefix in {"hl7", "w3c", "mitre", "openid", "icao", "dlms", "opc", "gs1"}:
                # These standards use readable namespace prefixes rather than a raw token transform.
                assert func_key.split("_", 1)[0] in {
                    "hl7v2",
                    "fhir",
                    "w3c",
                    "mitre",
                    "oidc",
                    "icao9303",
                    "dlms",
                    "opcua",
                    "gs1",
                    "stix21",
                }
            elif standard.startswith("ISO"):
                assert func_key.startswith("iso")
            elif standard.startswith("RFC"):
                assert func_key.startswith("rfc")
            elif standard.startswith("STIX"):
                assert func_key.startswith("stix21_")
            elif standard == "CVE":
                assert func_key.startswith("cve_")
            elif standard == "DICOM":
                assert func_key.startswith("dicom_")
            elif standard == "EPSG":
                assert func_key.startswith("epsg_")


def test_function_catalog_mentions_every_public_sql_udf() -> None:
    catalog = (ROOT / "docs" / "FUNCTION_CATALOG.md").read_text(encoding="utf-8")
    missing = sorted(name for name in PUBLIC_FUNCTIONS if f"`{name}`" not in catalog)
    assert not missing, f"public UDFs missing from function catalog: {missing}"


def test_function_catalog_uses_standard_first_display_names() -> None:
    catalog = (ROOT / "docs" / "FUNCTION_CATALOG.md").read_text(encoding="utf-8")
    missing = sorted(
        func_key
        for func_key, metadata in PUBLIC_FUNCTIONS.items()
        if metadata["name"] not in catalog
    )
    assert not missing, f"public display names missing from catalog: {missing}"
