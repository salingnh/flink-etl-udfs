"""Build a Flink ``python.files`` ZIP with ``flink_etl_udfs`` at archive root."""

from __future__ import annotations

import argparse
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = ROOT / "src" / "flink_etl_udfs"
DEFAULT_OUTPUT = ROOT / "dist" / "flink_etl_udfs.zip"


def build_python_files_zip(output: Path) -> Path:
    """Create a ZIP importable as ``flink_etl_udfs`` by Flink Python workers."""
    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    with ZipFile(output, "w", compression=ZIP_DEFLATED) as archive:
        for source in sorted(PACKAGE_ROOT.rglob("*.py")):
            relative = source.relative_to(PACKAGE_ROOT.parent)
            archive.write(source, relative.as_posix())

    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Output ZIP path (default: dist/flink_etl_udfs.zip)",
    )
    args = parser.parse_args()
    artifact = build_python_files_zip(args.output)
    print(artifact)


if __name__ == "__main__":
    main()
