"""Smoke-test SQL UDF registration/execution against the installed PyFlink runtime."""

from __future__ import annotations

import argparse
from pathlib import Path

from pyflink.table import EnvironmentSettings, TableEnvironment


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", type=Path)
    args = parser.parse_args()

    artifact = args.artifact.resolve()
    if not artifact.exists():
        raise SystemExit(f"artifact does not exist: {artifact}")

    table_env = TableEnvironment.create(EnvironmentSettings.in_batch_mode())
    table_env.get_config().set("python.files", artifact.as_uri())

    table_env.execute_sql(
        """
        CREATE TEMPORARY SYSTEM FUNCTION VN_NORMALIZE_MOBILE_PHONE
        AS 'flink_etl_udfs.udfs.vietnam.normalize_vn_mobile_phone'
        LANGUAGE PYTHON
        """
    )
    table_env.execute_sql(
        """
        CREATE TEMPORARY SYSTEM FUNCTION ENRICH_EXTRACT_PROFILE_URL
        AS 'flink_etl_udfs.udfs.enrichment.extract_profile_url'
        LANGUAGE PYTHON
        """
    )

    result = table_env.execute_sql(
        "SELECT VN_NORMALIZE_MOBILE_PHONE('0169 123 4567')"
    )
    with result.collect() as rows:
        row = next(rows)

    if row[0] != "0391234567":
        raise AssertionError(f"unexpected Vietnam phone UDF result: {row[0]!r}")


if __name__ == "__main__":
    main()
