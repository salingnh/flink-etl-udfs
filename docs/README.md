# Tài liệu

Thư mục này chứa research, hướng dẫn deployment và catalog toàn bộ PyFlink SQL UDF của `flink-etl-udfs`.

## Research và kiến trúc

- [Tổng quan ETL research](ETL_RESEARCH.md)
- [Ma trận lĩnh vực / loại dữ liệu / ETL](research/domain-matrix.md)
- [OSINT research](research/osint.md)
- [Rà soát tính generic và hướng migration](GENERICITY_REVIEW.md)

## Deployment

- [Hướng dẫn Python dependency và deploy lên Flink cluster](DEPLOYMENT.md)

Repository tách dependency theo mục đích:

- `requirements.txt` — package third-party thực sự được worker-side UDF import, phù hợp cho Flink `--pyRequirements`.
- `requirements-flink.txt` — pin `apache-flink` cho custom Python image/virtualenv cần tự cung cấp PyFlink.
- `requirements-dev.txt` — test, lint, type-check và build dependency.

## Danh mục function

- [Tổng quan function catalog](FUNCTION_CATALOG.md)
- [Generic / Default / P0 common](functions/default-common.md)
- [OSINT](functions/osint.md)
- [Việt Nam: dân cư, thuế, giáo dục, ngân hàng](functions/vietnam.md)
- [Chuẩn quốc tế và domain chuyên ngành](functions/standards.md)

Mỗi SQL UDF trong `src/flink_etl_udfs/registry.py` phải có tài liệu gồm:

- tên hiển thị tiếng Việt;
- tên SQL function và signature;
- chuẩn/phạm vi validation;
- mô tả semantics;
- ví dụ giá trị trước → sau transform;
- ví dụ SQL sử dụng.

Public core Python transforms đồng thời phải có source-level docstring/comment và unit test.
