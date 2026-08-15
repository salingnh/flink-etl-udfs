# Tài liệu

Thư mục này chứa research, deployment guide và catalog của public PyFlink SQL UDF.

## Contract và triết lý transform

- [ETL normalization philosophy](NORMALIZATION_PHILOSOPHY.md) — normalizer = TRY_CAST → deterministic TRY_PARSE → semantic validation → canonical output; invalid/ambiguous → NULL.
- [Public UDF contract](PUBLIC_UDF_CONTRACT.md) — category, TRY_CAST boundary, error policy và sample-driven metadata contract.

## Research và kiến trúc

- [Tổng quan ETL research](ETL_RESEARCH.md)
- [Ma trận lĩnh vực / loại dữ liệu / ETL](research/domain-matrix.md)
- [OSINT research](research/osint.md)
- [Rà soát và cleanup tính generic](GENERICITY_REVIEW.md)

## Deployment

- [Python dependency và deploy lên Flink cluster](DEPLOYMENT.md)

## Public function catalog

- [Danh mục 66 public UDF và standard-first naming](FUNCTION_CATALOG.md)
- `src/flink_etl_udfs/public_api.py` là machine-readable source of truth cho SQL name, display name và Python entrypoint.

Version `0.7.0` là breaking cleanup: loại `registry.py`, không giữ compatibility alias, đổi các function gắn với chuẩn sang tên `<standard>_<operation>_<subject>` và bổ sung nhóm ICAO/ISO/RFC/W3C/OIDC từ identity/identifier catalog.
