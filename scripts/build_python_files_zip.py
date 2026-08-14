"""Build a Flink ``python.files`` ZIP with an importable package root."""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = ROOT / "src" / "flink_etl_udfs"
REQUIREMENTS = ROOT / "requirements.txt"
DEFAULT_OUTPUT = ROOT / "dist" / "flink_etl_udfs.zip"


def _write_tree(archive: ZipFile, source_root: Path, archive_root: Path) -> None:
    for source in sorted(source_root.rglob("*")):
        if not source.is_file() or "__pycache__" in source.parts:
            continue
        relative = source.relative_to(source_root)
        archive.write(source, (archive_root / relative).as_posix())


def build_python_files_zip(output: Path, *, vendor_requirements: bool = False) -> Path:
    """Create a ZIP importable by Flink Python workers.

    Tests call this with ``vendor_requirements=False`` to stay offline. Production
    CLI builds vendor ``requirements.txt`` by default so SQL Gateway can use only
    ``SET 'python.files' = '...zip'`` without pre-installing reference-data packages.
    """
    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="flink-etl-udfs-") as temp_dir:
        vendor_root = Path(temp_dir) / "vendor"
        if vendor_requirements:
            vendor_root.mkdir(parents=True, exist_ok=True)
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "--disable-pip-version-check",
                    "--no-compile",
                    "--target",
                    str(vendor_root),
                    "-r",
                    str(REQUIREMENTS),
                ],
                check=True,
            )

        with ZipFile(output, "w", compression=ZIP_DEFLATED) as archive:
            _write_tree(archive, PACKAGE_ROOT, Path("flink_etl_udfs"))
            if vendor_requirements:
                _write_tree(archive, vendor_root, Path("."))

    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Output ZIP path (default: dist/flink_etl_udfs.zip)",
    )
    parser.add_argument(
        "--no-vendor-requirements",
        action="store_true",
        help="Do not vendor requirements.txt into the ZIP.",
    )
    args = parser.parse_args()
    artifact = build_python_files_zip(
        args.output,
        vendor_requirements=not args.no_vendor_requirements,
    )
    print(artifact)


if __name__ == "__main__":
    main()
