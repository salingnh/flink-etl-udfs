# Documentation

This directory contains the design/research record, deployment guidance, and callable UDF reference for `flink-etl-udfs`.

## Research

- [ETL research overview](ETL_RESEARCH.md)
- [Cross-domain data/ETL research matrix](research/domain-matrix.md)
- [OSINT research](research/osint.md)

## Deployment

- [Flink Python dependency and cluster deployment guide](DEPLOYMENT.md)

The repository separates dependency files by purpose:

- `requirements.txt` — third-party packages imported by worker-side UDF code and suitable for Flink `--pyRequirements`.
- `requirements-flink.txt` — pinned `apache-flink` package for custom Python images/virtualenvs that must provide PyFlink themselves.
- `requirements-dev.txt` — local test, lint, type-check, and build dependencies.

## Function reference

- [Function catalog overview](FUNCTION_CATALOG.md)
- [Default + P0 common functions](functions/default-common.md)
- [OSINT functions](functions/osint.md)
- [Vietnam / citizen / education / banking functions](functions/vietnam.md)
- [Standards and specialized-domain functions](functions/standards.md)

The function catalog covers every SQL UDF registered in `src/flink_etl_udfs/registry.py`. Public core Python transforms also carry source-level docstrings.
