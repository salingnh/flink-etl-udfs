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
phone = importlib.import_module("flink_etl_udfs.udfs.vietnam")

assert enrichment.extract_profile_url["function"].__module__ == "flink_etl_udfs.enrichment.profile"
assert enrichment.extract_profile_url["function"].__name__ == "extract_profile_url_sync"
assert enrichment.extract_profile_url["deterministic"] is False

assert phone.normalize_vn_mobile_phone["function"].__module__ == "flink_etl_udfs.core.vietnam"
assert phone.normalize_vn_mobile_phone["function"].__name__ == "normalize_vn_mobile_phone_value"
assert phone.normalize_vn_mobile_phone["deterministic"] is True
'''

    subprocess.run(
        [sys.executable, "-S", "-c", code, str(artifact)],
        check=True,
        cwd=tmp_path,
    )
