# Tài liệu

Thư mục này chứa research, deployment guide và catalog của public PyFlink SQL UDF.

## Research và kiến trúc

- [Tổng quan ETL research](ETL_RESEARCH.md)
- [Ma trận lĩnh vực / loại dữ liệu / ETL](research/domain-matrix.md)
- [OSINT research](research/osint.md)
- [Rà soát và cleanup tính generic](GENERICITY_REVIEW.md)

## Deployment

- [Python dependency và deploy lên Flink cluster](DEPLOYMENT.md)

## Danh mục function

- [Tổng quan function catalog](FUNCTION_CATALOG.md)
- [Generic / Default / P0 common](functions/default-common.md)
- [Internet, Security / CTI và Source Code](functions/internet-security-code.md)
- [OSINT](functions/osint.md)
- [External enrichment / REST lookup](functions/enrichment.md)
- [Việt Nam: dân cư, thuế và số di động](functions/vietnam.md)
- [Chuẩn quốc tế và domain chuyên ngành](functions/standards.md)

Version `0.5.0` không giữ compatibility alias. Version `0.6.0` bổ sung Vietnam mobile migration normalization và REST enrichment ban đầu. Version `0.6.1` chỉnh profile enrichment thành scalar UDF đồng bộ tương thích Flink 2.2.1 SQL Gateway mà không khôi phục các alias đã xóa.

Mỗi SQL UDF còn lại phải có tên hiển thị tiếng Việt, phạm vi validation, mô tả semantics, ví dụ trước → sau, SQL usage, core/client docstring/comment và unit test hoặc mocked-I/O test.
