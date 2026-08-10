# Danh mục hàm ETL / PyFlink UDF

Repository dùng kiến trúc `pure Python core transform → thin PyFlink wrapper → SQL registry name` và ưu tiên **generic/standard-first** thay vì tạo UDF theo tên dataset.

## Quy ước đặt tên

- `etl_*`: transform generic dùng giữa nhiều lĩnh vực.
- `net_*`: domain, URL, DNS, ASN, MIME.
- `security_*`: hash/CVE; `cti_*`: STIX/MITRE ATT&CK.
- `code_*`: repository URL và Git object ID.
- `osint_*`: chỉ semantics thật sự của OSINT observation/account handle.
- `vn_*`: chỉ cấu trúc định danh thật sự đặc thù Việt Nam.
- `finance_*`, `health_*`, `supply_*`, `iot_*`, `geo_*`: chuẩn/domain chuyên ngành rõ ràng.

Không có compatibility alias trong `0.5.0`. Các tên legacy/dataset-specific đã bị xóa thay vì giữ wrapper chuyển tiếp.

## Mức validation

1. **Canonicalization**: đưa giá trị về representation ổn định.
2. **Syntax validation**: kiểm tra hình thức, không xác minh registry.
3. **Checksum validation**: kiểm tra mod/check digit khi implementation hỗ trợ.
4. **Reference-data validation**: phải join/lookup nguồn versioned có thẩm quyền, không hard-code vào scalar UDF.

## Chuẩn được ưu tiên

ISO 8601, ITU-T E.164, ISO 4217, ISO 13616, ISO 9362, ISO 17442, ISO 20022, Unicode NFC, GS1 GTIN/SSCC/EPCIS, STIX, MITRE ATT&CK, FHIR, HL7 v2, DICOM, OPC UA, DLMS/COSEM và EPSG.

## Đăng ký

```python
from flink_etl_udfs.registry import register_all_udfs

register_all_udfs(t_env)
```

Production nên đăng ký domain pack tối thiểu cần thiết.

## Catalog

- [Generic / Default / P0 common](functions/default-common.md)
- [Internet, Security / CTI và Source Code](functions/internet-security-code.md)
- [OSINT](functions/osint.md)
- [Việt Nam: dân cư và thuế](functions/vietnam.md)
- [Chuẩn quốc tế và domain chuyên ngành](functions/standards.md)
- [Rà soát cleanup / genericity](GENERICITY_REVIEW.md)

## Coverage

Documented SQL UDFs: **67**.

UDF mới bắt buộc có core docstring/comment, test valid/invalid/NULL, registry entry, tên hiển thị tiếng Việt, mô tả mức validation, ví dụ input → output và SQL usage.
