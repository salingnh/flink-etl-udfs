"""Packaging smoke tests for the ZIP referenced by Flink ``python.files``."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
BUILDER_PATH = ROOT / "scripts" / "build_python_files_zip.py"


def _load_builder():
    spec = importlib.util.spec_from_file_location("build_python_files_zip", BUILDER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_python_files_zip_has_importable_package_root(tmp_path: Path) -> None:
    builder = _load_builder()
    artifact = builder.build_python_files_zip(tmp_path / "flink_etl_udfs.zip")

    with ZipFile(artifact) as archive:
        names = set(archive.namelist())

    assert "flink_etl_udfs/__init__.py" in names
    assert "flink_etl_udfs/udfs/enrichment.py" in names
    assert "flink_etl_udfs/udfs/vietnam.py" in names
    assert "flink_etl_udfs/udfs/standards.py" in names
    assert "flink_etl_udfs/public_api.py" in names
    assert not any(name.startswith("src/") for name in names)


def test_priority_sql_entrypoints_resolve_from_zip_only(tmp_path: Path) -> None:
    builder = _load_builder()
    artifact = builder.build_python_files_zip(tmp_path / "flink_etl_udfs.zip")

    code = r'''
import importlib
import sys
import types


def fake_udf(function, input_types=None, result_type=None, deterministic=None, **kwargs):
    return {
        "function": function,
        "input_types": input_types,
        "result_type": result_type,
        "deterministic": deterministic,
    }

pyflink = types.ModuleType("pyflink")
table = types.ModuleType("pyflink.table")
udf_module = types.ModuleType("pyflink.table.udf")
udf_module.udf = fake_udf
table.udf = udf_module
pyflink.table = table
sys.modules["pyflink"] = pyflink
sys.modules["pyflink.table"] = table
sys.modules["pyflink.table.udf"] = udf_module

sys.path.insert(0, sys.argv[1])

enrichment = importlib.import_module("flink_etl_udfs.udfs.enrichment")
vietnam = importlib.import_module("flink_etl_udfs.udfs.vietnam")
standards = importlib.import_module("flink_etl_udfs.udfs.standards")
public_api = importlib.import_module("flink_etl_udfs.public_api")

assert enrichment.extract_profile_url["function"].__module__ == "flink_etl_udfs.enrichment.profile"
assert enrichment.extract_profile_url["function"].__name__ == "extract_profile_url_sync"
assert enrichment.extract_profile_url["deterministic"] is False

assert vietnam.normalize_vn_mobile_phone["function"].__module__ == "flink_etl_udfs.udfs.vietnam"
assert vietnam.normalize_vn_mobile_phone["function"].__name__ == "_normalize_vn_mobile_phone"
assert vietnam.normalize_vn_mobile_phone["deterministic"] is True
assert "flink_etl_udfs.core.vietnam" not in sys.modules

assert standards.iso2108_normalize_isbn13["function"].__name__ == "normalize_iso2108_isbn13_value"
assert standards.rfc9562_normalize_uuid["function"].__name__ == "normalize_rfc9562_uuid_value"
assert standards.iso3166_normalize_alpha3["function"].__name__ == "normalize_iso3166_alpha3_value"
assert public_api.PUBLIC_FUNCTIONS["iso2108_normalize_isbn13"]["entrypoint"] == (
    "flink_etl_udfs.udfs.standards.iso2108_normalize_isbn13"
)
'''

    subprocess.run(
        [sys.executable, "-S", "-c", code, str(artifact)],
        check=True,
        cwd=tmp_path,
    )
