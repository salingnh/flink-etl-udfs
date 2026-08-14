# Tài liệu

Thư mục này chứa research, deployment guide và catalog của public PyFlink SQL UDF.

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
