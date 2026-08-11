# Danh mục hàm ETL / PyFlink UDF

Repository dùng kiến trúc `pure Python core transform → thin PyFlink wrapper → SQL registry name` cho transform deterministic, và tách riêng `async enrichment client → async PyFlink UDF` cho external I/O. Thiết kế ưu tiên **generic/standard-first** thay vì tạo UDF theo tên dataset.

## Quy ước đặt tên

- `etl_*`: transform generic dùng giữa nhiều lĩnh vực.
- `net_*`: domain, URL, DNS, ASN, MIME.
- `security_*`: hash/CVE; `cti_*`: STIX/MITRE ATT&CK.
- `code_*`: repository URL và Git object ID.
- `osint_*`: semantics deterministic của OSINT observation/account handle.
- `enrich_*`: external async enrichment; có network I/O và không deterministic.
- `vn_*`: quy tắc thật sự đặc thù Việt Nam như CMND/CCCD, MST và lịch sử đổi đầu số di động.
- `finance_*`, `health_*`, `supply_*`, `iot_*`, `geo_*`: chuẩn/domain chuyên ngành rõ ràng.

Không có compatibility alias trong `0.6.0`. Các tên legacy/dataset-specific đã bị xóa thay vì giữ wrapper chuyển tiếp.

## Mức validation

1. **Canonicalization**: đưa giá trị về representation ổn định.
2. **Syntax validation**: kiểm tra hình thức, không xác minh registry.
3. **Checksum validation**: kiểm tra mod/check digit khi implementation hỗ trợ.
4. **Reference-data validation**: phải join/lookup nguồn versioned có thẩm quyền, không hard-code vào scalar UDF.
5. **External enrichment**: gọi service/API bên ngoài; phải khai báo nondeterministic và có timeout/retry/concurrency policy.

## Chuẩn được ưu tiên

ISO 8601, ITU-T E.164, ISO 4217, ISO 13616, ISO 9362, ISO 17442, ISO 20022, Unicode NFC, GS1 GTIN/SSCC/EPCIS, STIX, MITRE ATT&CK, FHIR, HL7 v2, DICOM, OPC UA, DLMS/COSEM và EPSG.

## Đăng ký

```python
from flink_etl_udfs.registry import register_all_udfs

register_all_udfs(t_env)
```

Production nên đăng ký domain pack tối thiểu cần thiết. Riêng `register_enrichment_udfs` chỉ nên bật khi TaskManager/Python worker có network route tới external service.

## Catalog

- [Generic / Default / P0 common](functions/default-common.md)
- [Internet, Security / CTI và Source Code](functions/internet-security-code.md)
- [OSINT](functions/osint.md)
- [External enrichment / REST lookup](functions/enrichment.md)
- [Việt Nam: dân cư, thuế và số di động](functions/vietnam.md)
- [Chuẩn quốc tế và domain chuyên ngành](functions/standards.md)
- [Rà soát cleanup / genericity](GENERICITY_REVIEW.md)

## Coverage

Documented SQL UDFs: **69**.

UDF mới bắt buộc có core/client docstring/comment, test valid/invalid/NULL hoặc mocked I/O, registry entry, tên hiển thị tiếng Việt, mô tả mức validation, ví dụ input → output và SQL usage.
