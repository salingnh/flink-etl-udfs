# Generic / Default / P0 Common Functions

Nhóm này nên được ưu tiên trước khi tạo function riêng cho một domain. Các ví dụ dùng dữ liệu quen thuộc như họ tên, số điện thoại, mã hồ sơ, số tài khoản và payload nghiệp vụ, nhưng logic **không phụ thuộc dataset cụ thể**.

## Default cross-domain helpers

Đăng ký bằng `register_default_udfs(t_env)`.

| Tên hiển thị | SQL function | Chuẩn / phạm vi | Mô tả | Giá trị trước → sau | Ví dụ SQL |
| --- | --- | --- | --- | --- | --- |
| Chỉ giữ chữ số | `digits_only` | Generic text cleanup | Chỉ giữ ASCII digit `0-9`; trả `NULL` nếu không còn chữ số. Phù hợp bước tiền xử lý mã/số điện thoại trước validator chuyên biệt. | `+84 (912) 345-678` → `84912345678` | `SELECT digits_only('+84 (912) 345-678');` |
| Che email | `mask_email` | Privacy / display masking | Che phần local của email nhưng giữ domain để hỗ trợ log/đối soát không lộ toàn bộ địa chỉ. Không phải email validator. | `nguyen.van.an@example.gov.vn` → `n***********n@example.gov.vn` | `SELECT mask_email(email);` |
| Che chuỗi ký tự | `mask_text` | Privacy / display masking | Che phần giữa chuỗi, giữ ký tự đầu/cuối. Dùng cho CCCD, tài khoản, mã hồ sơ khi hiển thị. | `034190006609` → `0**********9` | `SELECT mask_text(citizen_id);` |
| Chuẩn hóa CIDR | `normalize_cidr` | IPv4 / IPv6 CIDR | Chuẩn hóa network CIDR và xóa host bits. Input sai trả `NULL`. | `10.20.30.45/24` → `10.20.30.0/24` | `SELECT normalize_cidr(source_network);` |
| Chuẩn hóa email | `normalize_email` | Internet email normalization | Trim và lowercase **chỉ phần domain**, giữ nguyên local part vì semantics case có thể phụ thuộc provider. | ` Nguyen.VanAn@EXAMPLE.GOV.VN ` → `Nguyen.VanAn@example.gov.vn` | `SELECT normalize_email(email);` |
| Chuẩn hóa địa chỉ IP | `normalize_ip` | IPv4 / IPv6 | Đưa IPv4/IPv6 về biểu diễn canonical/compressed. | `2001:0db8:0:0:0:0:0:1` → `2001:db8::1` | `SELECT normalize_ip(source_ip);` |
| Chuẩn hóa Unicode NFC | `normalize_unicode_nfc` | Unicode NFC | Hợp nhất các biểu diễn Unicode tương đương về NFC mà không đổi hoa/thường. Quan trọng với tên người tiếng Việt. | Unicode decomposed `Nguyễn` → NFC `Nguyễn` | `SELECT normalize_unicode_nfc(full_name);` |
| Chuẩn hóa khoảng trắng | `normalize_whitespace` | Generic text | Gộp chuỗi whitespace liên tiếp thành một dấu cách và trim hai đầu. | `  Nguyễn   Văn\nAn  ` → `Nguyễn Văn An` | `SELECT normalize_whitespace(full_name);` |
| Blank thành NULL | `null_if_blank` | Data quality | Chuỗi rỗng/chỉ có whitespace được chuyển thành `NULL`. | `   ` → `NULL` | `SELECT null_if_blank(raw_value);` |
| Fingerprint SHA-256 | `sha256_fingerprint` | SHA-256 deterministic fingerprint | Tạo fingerprint ổn định phục vụ matching/dedup không cần giữ raw ID trong khóa. Không dùng thay password hashing/KDF. | `034190006609` → `fb24878d21dd3455612ac4d28ff33e5a63d771df078cf548339db7a026d8f35e` | `SELECT sha256_fingerprint(citizen_id);` |
| Trim text | `trim_text` | Generic text | Bỏ whitespace đầu/cuối, giữ `NULL`. | `  0101234567  ` → `0101234567` | `SELECT trim_text(tax_id);` |

## P0 common ETL

Đăng ký bằng `register_common_udfs(t_env)`.

| Tên hiển thị | SQL function | Chuẩn / phạm vi | Mô tả | Giá trị trước → sau | Ví dụ SQL |
| --- | --- | --- | --- | --- | --- |
| Chuẩn hóa JSON canonical | `etl_canonicalize_json` | JSON canonicalization nội bộ | Parse JSON rồi xuất compact JSON với object key được sort ổn định. Hữu ích cho hash, dedup và so sánh payload. | `{"name":"Công ty A","mst":"0101234567"}` → `{"mst":"0101234567","name":"Công ty A"}` | `SELECT etl_canonicalize_json(payload);` |
| Làm phẳng JSON | `etl_flatten_json` | Generic nested JSON | Chuyển JSON lồng nhau thành dotted/indexed paths, phù hợp OCR/API payload trước khi map sang bảng. | `{"address":{"province":"Hà Nội","ward":"Phúc Xá"}}` → `{"address.province":"Hà Nội","address.ward":"Phúc Xá"}` | `SELECT etl_flatten_json(payload);` |
| Kiểm tra JSON hợp lệ | `etl_is_valid_json` | JSON syntax validation | Trả `TRUE` nếu non-null input parse được thành JSON. | `{"cccd":"034190006609"}` → `TRUE` | `SELECT etl_is_valid_json(payload);` |
| Khóa tìm kiếm tên Latin | `etl_latin_name_search_key` | Generic Latin-script search key | Bỏ dấu/đưa lowercase/tokenize cho tên dùng bảng chữ cái Latin. Chỉ dùng blocking/search, không coi là canonical identity. | `Đặng Thị Hồng` → `dang thi hong` | `SELECT etl_latin_name_search_key(full_name);` |
| Chuẩn hóa mã tài khoản/tham chiếu | `etl_normalize_account_identifier` | Generic alphanumeric identifier | Bỏ space/dot/hyphen và uppercase mã chữ-số. Dùng cho account/reference ID nội bộ; **không thay IBAN hoặc validator ngân hàng**. | `001-234.567 890` → `001234567890` | `SELECT etl_normalize_account_identifier(account_ref);` |
| Chuẩn hóa địa chỉ dạng text | `etl_normalize_address_text` | Generic address preprocessing | Chuẩn hóa Unicode, whitespace và khoảng cách quanh dấu phân cách; không tự đoán tỉnh/huyện/xã hoặc geocode. | `12 Nguyễn Trãi,   P. Bến Thành` → `12 Nguyễn Trãi, P. Bến Thành` | `SELECT etl_normalize_address_text(address);` |
| Chuẩn hóa mã tiền tệ | `etl_normalize_currency_code` | ISO 4217 **shape-only** | Chuẩn hóa mã 3 chữ cái sang uppercase. Membership trong danh mục ISO 4217 hiện hành cần reference-data lookup. | `vnd` → `VND` | `SELECT etl_normalize_currency_code(currency);` |
| Chuẩn hóa ngày ISO | `etl_normalize_date` | ISO 8601 calendar date | Validate và xuất ngày dạng `YYYY-MM-DD`. | `2026-08-10` → `2026-08-10` | `SELECT etl_normalize_date(issue_date);` |
| Chuẩn hóa số Decimal | `etl_normalize_decimal` | Exact decimal | Chuẩn hóa số dạng text bằng `Decimal`, loại zero thừa và tránh sai số binary float. Phù hợp số tiền/thuế/phí. | `001250000.5000` → `1250000.5` | `SELECT etl_normalize_decimal(amount);` |
| Chuẩn hóa điện thoại E.164 | `etl_normalize_e164` | ITU-T E.164 shape | Chuyển số quốc tế/quốc nội về dạng `+<country><number>` khi cung cấp default country code. Không lookup carrier. | `0912 345 678`, `+84` → `+84912345678` | `SELECT etl_normalize_e164(phone, '+84');` |
| Chuẩn hóa mã nghiệp vụ | `etl_normalize_identifier_code` | Generic business identifier | Remove whitespace, uppercase và kiểm tra tập ký tự bảo thủ `A-Z 0-9 . _ / -`. Dùng chung cho mã trường, mã hồ sơ, mã khách hàng, mã tài sản... | ` hs- 2026 / 001 ` → `HS-2026/001` | `SELECT etl_normalize_identifier_code(record_code);` |
| Chuẩn hóa timestamp ISO về UTC | `etl_normalize_iso_datetime` | ISO 8601 + UTC | Nhận timestamp có timezone/offset, chuyển về UTC `Z`. Timestamp không timezone bị reject để tránh tự đoán sai. | `2026-08-10T14:30:00+07:00` → `2026-08-10T07:30:00.000000Z` | `SELECT etl_normalize_iso_datetime(updated_at);` |
| Chuẩn hóa textual NULL | `etl_normalize_null_token` | Generic ingestion | Trim và đổi các marker như `null`, `N/A`, `[NULL]`, `undefined` thành `NULL`. | `[NULL]` → `NULL` | `SELECT etl_normalize_null_token(raw_value);` |
| Chuẩn hóa phần trăm | `etl_normalize_percentage` | Numeric 0..100 | Bỏ `%`, chuẩn hóa Decimal và chỉ chấp nhận miền `0..100`. | `25.50%` → `25.5` | `SELECT etl_normalize_percentage(ownership_pct);` |
| Chuẩn hóa tên người | `etl_normalize_person_name` | Unicode NFC + whitespace | Chuẩn hóa tên người theo Unicode NFC và whitespace, giữ nguyên case và không giả định thứ tự họ/tên theo quốc gia. | `  Nguyễn   Văn   An ` → `Nguyễn Văn An` | `SELECT etl_normalize_person_name(full_name);` |
| Chuẩn hóa xác suất/score | `etl_normalize_probability` | Numeric 0..1 | Parse finite number trong miền `0..1`; loại `NaN`, infinity và out-of-range. | `0.82` → `0.82` | `SELECT etl_normalize_probability(match_score);` |
| Kiểm tra trường có dữ liệu | `etl_quality_is_present` | Data quality | `TRUE` khi giá trị không phải `NULL`, blank hoặc null-token phổ biến. | ` N/A ` → `FALSE` | `SELECT etl_quality_is_present(citizen_id);` |
| Kiểm tra số trong khoảng | `etl_quality_number_in_range` | Data quality / Decimal | Kiểm tra giá trị Decimal trong khoảng min/max inclusive. | `105`, min `0`, max `100` → `FALSE` | `SELECT etl_quality_number_in_range(score, '0', '100');` |
| Tạo record ID ổn định | `etl_stable_record_id` | SHA-256 provenance key | Hash deterministic từ `source` + `natural_key`, phù hợp idempotent load/dedup giữa nhiều nguồn. | `crm`, `034190006609` → `29cd4c451f2ee999eafb9dc4dd6c50b4b77c21967a672acbb803a6752618802c` | `SELECT etl_stable_record_id(source_system, natural_key);` |

## Gợi ý sử dụng

Nếu logic của bạn chỉ là chuẩn hóa một mã nghiệp vụ, **không tạo** các UDF mới kiểu `normalize_customer_code`, `normalize_teacher_code`, `normalize_case_code`. Hãy dùng `etl_normalize_identifier_code` và để semantics của mã nằm ở schema/data contract.

Tương tự, dùng `etl_normalize_person_name` và `etl_normalize_address_text` làm bước canonicalization chung; parsing theo quốc gia hoặc lookup mã hành chính nên thực hiện ở domain/reference-data layer.
