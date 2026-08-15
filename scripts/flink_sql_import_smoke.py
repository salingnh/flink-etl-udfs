"""Smoke-test SQL UDF registration/execution against the installed PyFlink runtime."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from pyflink.table import EnvironmentSettings, TableEnvironment


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", type=Path)
    args = parser.parse_args()

    artifact = args.artifact.resolve()
    if not artifact.exists():
        raise SystemExit(f"artifact does not exist: {artifact}")

    sys.path.insert(0, str(artifact))

    table_env = TableEnvironment.create(EnvironmentSettings.in_batch_mode())
    table_env.add_python_file(str(artifact))

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

    # VARCHAR follows the original transform semantics.
    result = table_env.execute_sql(
        "SELECT VN_NORMALIZE_MOBILE_PHONE('0169 123 4567')"
    )
    with result.collect() as rows:
        row = next(rows)
    if row[0] != "0391234567":
        raise AssertionError(f"unexpected VARCHAR phone result: {row[0]!r}")

    # BIGINT is deliberately not pre-cast in SQL. The Python UDF receives it and
    # internally TRY_CASTs it to STRING before running the same phone logic.
    result = table_env.execute_sql(
        "SELECT VN_NORMALIZE_MOBILE_PHONE(CAST(84912345678 AS BIGINT))"
    )
    with result.collect() as rows:
        row = next(rows)
    if row[0] != "0912345678":
        raise AssertionError(f"unexpected BIGINT phone result: {row[0]!r}")

    # Other SQL scalar types must also pass planner validation. Their internal
    # STRING cast succeeds, but the phone parser rejects the resulting value -> NULL.
    result = table_env.execute_sql(
        """
        SELECT
            VN_NORMALIZE_MOBILE_PHONE(TRUE),
            VN_NORMALIZE_MOBILE_PHONE(DATE '2026-08-15')
        """
    )
    with result.collect() as rows:
        row = next(rows)
    if row[0] is not None or row[1] is not None:
        raise AssertionError(f"invalid typed inputs must return NULL: {row!r}")


if __name__ == "__main__":
    main()
