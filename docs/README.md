# Documentation

This directory contains the design/research record and the callable UDF reference for `flink-etl-udfs`.

## Research

- [ETL research overview](ETL_RESEARCH.md)
- [Cross-domain data/ETL research matrix](research/domain-matrix.md)
- [OSINT research](research/osint.md)

## Function reference

- [Function catalog overview](FUNCTION_CATALOG.md)
- [Default + P0 common functions](functions/default-common.md)
- [OSINT functions](functions/osint.md)
- [Vietnam / citizen / education / banking functions](functions/vietnam.md)
- [Standards and specialized-domain functions](functions/standards.md)

The function catalog covers every SQL UDF registered in `src/flink_etl_udfs/registry.py`. Public core Python transforms also carry source-level docstrings.
