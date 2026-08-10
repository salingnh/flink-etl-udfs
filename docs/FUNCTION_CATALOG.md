# Danh mục hàm ETL / PyFlink UDF

Tài liệu này mô tả toàn bộ SQL UDF được đăng ký trong repository theo hướng dễ sử dụng cho Data Engineer Việt Nam, nhưng **không gắn logic generic vào một dataset cụ thể**.

Kiến trúc implementation vẫn giữ nguyên:

`pure Python core transform → thin PyFlink wrapper → SQL registry name`

## Quy ước đặt tên

- **SQL function name** tiếp tục dùng tiếng Anh, `snake_case`, ổn định cho code và backward compatibility.
- **Tên hiển thị** trong tài liệu dùng tiếng Việt để người vận hành dễ hiểu mục đích.
- Prefix `etl_` dành cho transform cross-domain/generic.
- Prefix `vn_` chỉ dành cho quy tắc thật sự phụ thuộc Việt Nam như CCCD/CMND, MST Việt Nam, số điện thoại profile `+84`.
- Prefix `finance_`, `health_`, `cti_`, `supply_`, `iot_`, `geo_`... dành cho chuẩn/nghiệp vụ chuyên ngành.
- Không tạo UDF mới chỉ vì tên cột của một dataset khác nhau. Nếu `ma_hoc_sinh`, `ma_giao_vien`, `customer_code`, `policy_code` cùng có logic chuẩn hóa dạng mã chữ-số, ưu tiên `etl_normalize_identifier_code`.

## Mức độ chuẩn hóa

Các mô tả trong catalog phân biệt rõ bốn mức:

1. **Canonicalization** — chỉ đưa cùng một giá trị về biểu diễn ổn định.
2. **Syntax validation** — kiểm tra cấu trúc/ký tự/độ dài nhưng chưa xác minh giá trị có tồn tại trong registry.
3. **Checksum validation** — có kiểm tra check digit/modulo khi implementation hỗ trợ.
4. **Reference-data validation** — cần join/lookup với danh mục có thẩm quyền; không hard-code danh mục thay đổi theo thời gian vào scalar UDF.

Ví dụ: `etl_normalize_currency_code('vnd')` trả `VND`, nhưng membership trong danh mục ISO 4217 hiện hành vẫn nên kiểm tra bằng reference data. Ngược lại `finance_normalize_iban` có kiểm tra mod-97.

## Chuẩn phổ biến được ưu tiên

- ISO 8601 cho ngày/giờ trao đổi dữ liệu.
- ITU-T E.164 cho hình thức số điện thoại quốc tế.
- ISO 4217 cho mã tiền tệ.
- ISO 13616 cho IBAN.
- ISO 9362 cho BIC.
- ISO 17442 cho LEI.
- ISO 20022 cho message identifier tài chính.
- GS1 GTIN/SSCC/EPCIS cho supply chain.
- Unicode NFC cho canonical text.
- STIX / MITRE ATT&CK cho CTI.
- FHIR / HL7 v2 / DICOM cho y tế.
- OPC UA và DLMS/COSEM cho industrial/IoT.
- GTFS và EPSG cho transport/geospatial.

## Hành vi chung

- Scalar normalizer giữ `NULL` và thông thường trả `NULL` với dữ liệu sai/không hỗ trợ thay vì throw exception trên từng record.
- Hàm quality kiểu Boolean trả `FALSE` với missing/invalid input.
- Search key / blocking key chỉ dùng để tạo candidate cho entity resolution, **không được coi là khẳng định hai bản ghi là cùng một thực thể**.
- Scalar UDF không thực hiện network/file I/O. Lookup registry, geocoding, RDAP, terminology service, sanctions list... phải chạy ở enrichment/reference-data layer.

## Đăng ký function

```python
from flink_etl_udfs.registry import register_all_udfs

register_all_udfs(t_env)
```

Production job nên đăng ký domain pack tối thiểu cần dùng thay vì `register_all_udfs()`.

## Catalog theo nhóm

- [Generic / Default / P0 common](functions/default-common.md)
- [OSINT](functions/osint.md)
- [Việt Nam: dân cư, thuế, giáo dục, ngân hàng](functions/vietnam.md)
- [Chuẩn quốc tế và domain chuyên ngành](functions/standards.md)
- [Rà soát tính generic và hướng migration](GENERICITY_REVIEW.md)

## Coverage

Documented SQL UDFs: **104**.

Khi thêm UDF mới, change bắt buộc phải có: core docstring/comment, test valid/invalid/NULL, registry entry, tên hiển thị tiếng Việt, mô tả mức validation, ví dụ input → output và SQL usage.
