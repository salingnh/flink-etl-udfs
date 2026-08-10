# Rà soát tính generic của thư viện

Mục tiêu của repository là xây dựng thư viện transform dùng lại được giữa nhiều hệ thống, không tạo một UDF riêng chỉ vì tên field hoặc dataset khác nhau.

## Nguyên tắc review

Một function chỉ nên mang prefix/domain riêng khi ít nhất một trong các yếu tố sau phụ thuộc domain:

- format quốc gia hoặc chuẩn ngành riêng;
- checksum/validation riêng của domain;
- vocabulary/code system riêng;
- semantics không thể diễn giải an toàn ở cross-domain layer.

Nếu function chỉ làm Unicode normalization, whitespace cleanup, uppercase code, remove separator, parse decimal... thì nên nằm ở `etl_*` generic layer.

## Các function đã được generic hóa

| Function/profile cũ | Generic function nên ưu tiên | Lý do |
| --- | --- | --- |
| `vn_normalize_name` | `etl_normalize_person_name` | Logic thực tế chỉ NFC + whitespace, không phụ thuộc Việt Nam. |
| `vn_name_search_key` | `etl_latin_name_search_key` | Logic là search/blocking key cho tên dùng Latin script; không nên gắn với một dataset dân cư cụ thể. |
| `vn_normalize_address` | `etl_normalize_address_text` | Chỉ normalize Unicode/whitespace/dấu phân cách, không lookup mã hành chính Việt Nam. |
| `vn_normalize_school_code` | `etl_normalize_identifier_code` | Mã trường, mã khách hàng, mã hồ sơ... cùng kiểu cleanup chữ-số. |
| `vn_normalize_teacher_code` | `etl_normalize_identifier_code` | Không có rule giáo viên riêng trong implementation. |
| `vn_normalize_student_code` | `etl_normalize_identifier_code` | Không có rule học sinh riêng trong implementation. |
| `vn_normalize_bank_account` | `etl_normalize_account_identifier` | Chỉ remove separator + uppercase; không phải validator tài khoản ngân hàng Việt Nam. |

Các tên `vn_*` trên **vẫn được giữ làm compatibility alias**, để job Flink hiện tại không bị break. Code mới nên dùng `etl_*` generic counterpart.

## Các function nên giữ domain-specific

| Function | Lý do giữ riêng |
| --- | --- |
| `vn_normalize_citizen_id` | Cấu trúc CMND/CCCD 9/12 chữ số là quy ước Việt Nam. |
| `vn_classify_identity_id` | Phân loại CMND/CCCD mang semantics Việt Nam. |
| `vn_normalize_tax_id` | Format MST 10 số / 10 số-3 số là profile Việt Nam. |
| `vn_classify_tax_id` | Phân biệt mã chính và đơn vị phụ thuộc dựa trên format MST Việt Nam. |
| `vn_normalize_phone` | Convenience profile của E.164 với default country code `+84`. |
| `vn_normalize_academic_year` | Semantics năm học liên tiếp phù hợp education profile, không phải ISO date. |
| `vn_normalize_sms_brandname` | Chỉ nên dùng trong telecom/Vietnam profile; constraint thực tế còn phụ thuộc operator. |
| `vn_build_entity_blocking_key` | Dùng search key Latin + phone profile `+84`; không phải generic global entity matcher. |

## Ưu tiên chuẩn quốc tế

### Ngày và thời gian

Ưu tiên `etl_normalize_iso_datetime` và `etl_normalize_date` cho dữ liệu trao đổi giữa hệ thống. Không tự đoán timezone khi source không cung cấp offset.

### Điện thoại

Ưu tiên `etl_normalize_e164(phone, default_country_code)` ở generic layer. `vn_normalize_phone` chỉ là convenience wrapper với `+84`.

### Tiền tệ

`etl_normalize_currency_code` chuẩn hóa hình thức 3 chữ cái theo ISO 4217. Vì danh mục currency code có thể được maintenance/update, việc xác minh code có tồn tại nên dùng reference-data table thay vì hard-code vào UDF.

### Tài chính quốc tế

- `finance_normalize_iban`: ISO 13616 + mod-97.
- `finance_normalize_bic`: ISO 9362 syntax.
- `finance_normalize_iso20022_message_type`: ISO 20022 message identifier.
- `osint_normalize_lei`: ISO 17442 + mod-97.

### Supply chain

- `supply_normalize_gtin`: GS1 GTIN-8/12/13/14 + check digit.
- `supply_normalize_sscc`: GS1 SSCC + check digit.
- `supply_normalize_epcis_event_type`: GS1 EPCIS event class.

## Những gì scalar UDF không nên làm

Không hard-code các danh mục thay đổi theo thời gian như:

- danh mục tỉnh/huyện/xã;
- mã trường do một hệ thống quản lý;
- danh sách ISO 4217 hiện hành;
- danh sách ngân hàng/BIC đang hoạt động;
- FHIR ValueSet/SNOMED/LOINC;
- ASN/RDAP ownership;
- sanctions/watchlist;
- danh sách CVE hoặc ATT&CK technique metadata.

Những dữ liệu này nên được version hóa thành reference table/broadcast state/lookup source và join trong pipeline.

## Migration guideline

Ví dụ code cũ:

```sql
SELECT
    vn_normalize_school_code(ma_truong),
    vn_normalize_teacher_code(ma_giao_vien),
    vn_normalize_student_code(ma_hoc_sinh)
FROM source_table;
```

Code mới generic hơn:

```sql
SELECT
    etl_normalize_identifier_code(ma_truong),
    etl_normalize_identifier_code(ma_giao_vien),
    etl_normalize_identifier_code(ma_hoc_sinh)
FROM source_table;
```

Khi sau này ingest `customer_code`, `policy_code`, `case_code` hoặc `asset_code`, vẫn dùng cùng transform thay vì tạo UDF mới theo tên dataset.
