# Generic / Default / P0 Common Functions

Nhóm này chứa các transform dùng chung giữa nhiều lĩnh vực. Ví dụ dùng dữ liệu dân cư, thuế và nghiệp vụ Việt Nam để dễ hình dung, nhưng logic không phụ thuộc một dataset cụ thể.

## Default cross-domain helpers

Đăng ký bằng `register_default_udfs(t_env)`.

| Tên hiển thị | SQL function | Chuẩn / phạm vi | Mô tả | Giá trị trước → sau | Ví dụ SQL |
| --- | --- | --- | --- | --- | --- |
| Chỉ giữ chữ số | `digits_only` | Generic text cleanup | Chỉ giữ ASCII digit `0-9`; trả `NULL` nếu không còn chữ số. | `+84 (912) 345-678` → `84912345678` | `SELECT digits_only(phone_raw);` |
| Che email | `mask_email` | Privacy masking | Che local-part nhưng giữ domain; không phải email validator. | `nguyen.van.an@example.gov.vn` → `n***********n@example.gov.vn` | `SELECT mask_email(email);` |
| Che chuỗi | `mask_text` | Privacy masking | Che phần giữa chuỗi và giữ ký tự đầu/cuối. | `034190006609` → `0**********9` | `SELECT mask_text(citizen_id);` |
| Chuẩn hóa CIDR | `normalize_cidr` | IPv4 / IPv6 CIDR | Canonicalize network CIDR và xóa host bits. | `10.20.30.45/24` → `10.20.30.0/24` | `SELECT normalize_cidr(source_network);` |
| Chuẩn hóa email | `normalize_email` | Email cleanup | Trim và lowercase domain, giữ nguyên local-part. | ` Nguyen.VanAn@EXAMPLE.GOV.VN ` → `Nguyen.VanAn@example.gov.vn` | `SELECT normalize_email(email);` |
| Chuẩn hóa IP | `normalize_ip` | IPv4 / IPv6 | Đưa địa chỉ IP về canonical/compressed representation. | `2001:0db8:0:0:0:0:0:1` → `2001:db8::1` | `SELECT normalize_ip(source_ip);` |
| Chuẩn hóa Unicode NFC | `normalize_unicode_nfc` | Unicode NFC | Hợp nhất các biểu diễn Unicode tương đương mà không đổi case. | decomposed `Nguyễn` → NFC `Nguyễn` | `SELECT normalize_unicode_nfc(full_name);` |
| Chuẩn hóa khoảng trắng | `normalize_whitespace` | Generic text | Gộp whitespace liên tiếp thành một space và trim. | `  Nguyễn   Văn\nAn  ` → `Nguyễn Văn An` | `SELECT normalize_whitespace(full_name);` |
| Blank thành NULL | `null_if_blank` | Data quality | Chuyển chuỗi rỗng/chỉ có whitespace thành `NULL`. | `   ` → `NULL` | `SELECT null_if_blank(raw_value);` |
| Fingerprint SHA-256 | `sha256_fingerprint` | SHA-256 | Tạo fingerprint deterministic cho dedup/matching; không dùng làm password hash. | `034190006609` → `SHA-256 64 ký tự` | `SELECT sha256_fingerprint(citizen_id);` |
| Trim text | `trim_text` | Generic text | Bỏ whitespace đầu/cuối và giữ `NULL`. | `  0101234567  ` → `0101234567` | `SELECT trim_text(tax_id);` |

## P0 common ETL

Đăng ký bằng `register_common_udfs(t_env)`.

| Tên hiển thị | SQL function | Chuẩn / phạm vi | Mô tả | Giá trị trước → sau | Ví dụ SQL |
| --- | --- | --- | --- | --- | --- |
| Chuẩn hóa JSON canonical | `etl_canonicalize_json` | JSON | Sort object keys và xuất compact JSON ổn định cho hash/dedup. | `{"name":"Công ty A","mst":"0101234567"}` → `{"mst":"0101234567","name":"Công ty A"}` | `SELECT etl_canonicalize_json(payload);` |
| Làm phẳng JSON | `etl_flatten_json` | Nested JSON | Chuyển nested JSON thành dotted/indexed paths. | `{"address":{"province":"Hà Nội"}}` → `{"address.province":"Hà Nội"}` | `SELECT etl_flatten_json(payload);` |
| Kiểm tra JSON | `etl_is_valid_json` | JSON syntax | Trả `TRUE` nếu input parse được thành JSON. | `{"cccd":"034190006609"}` → `TRUE` | `SELECT etl_is_valid_json(payload);` |
| Khóa tìm kiếm tên Latin | `etl_latin_name_search_key` | Entity-resolution blocking | Bỏ dấu, lowercase và tokenize cho candidate search; không phải canonical identity. | `Đặng Thị Hồng` → `dang thi hong` | `SELECT etl_latin_name_search_key(full_name);` |
| Chuẩn hóa địa chỉ text | `etl_normalize_address_text` | Address preprocessing | Chuẩn hóa Unicode, whitespace và separator; không tự suy đoán mã hành chính/geocode. | `12 Nguyễn Trãi,   P. Bến Thành` → `12 Nguyễn Trãi, P. Bến Thành` | `SELECT etl_normalize_address_text(address);` |
| Chuẩn hóa mã tiền tệ | `etl_normalize_currency_code` | ISO 4217 shape | Uppercase mã 3 chữ cái; membership hiện hành phải lookup reference data. | `vnd` → `VND` | `SELECT etl_normalize_currency_code(currency);` |
| Chuẩn hóa ngày | `etl_normalize_date` | ISO 8601 date | Validate và xuất `YYYY-MM-DD`. | `2026-08-10` → `2026-08-10` | `SELECT etl_normalize_date(issue_date);` |
| Chuẩn hóa Decimal | `etl_normalize_decimal` | Exact decimal | Loại zero thừa bằng `Decimal`, tránh sai số binary float. | `001250000.5000` → `1250000.5` | `SELECT etl_normalize_decimal(amount);` |
| Chuẩn hóa điện thoại | `etl_normalize_e164` | ITU-T E.164 shape | Chuyển national/international number về `+<country><number>` khi có default country code. | `0912 345 678`, `+84` → `+84912345678` | `SELECT etl_normalize_e164(phone, '+84');` |
| Chuẩn hóa mã nghiệp vụ | `etl_normalize_identifier_code` | Generic business code | Remove whitespace, uppercase và kiểm tra tập ký tự bảo thủ. | ` hs- 2026 / 001 ` → `HS-2026/001` | `SELECT etl_normalize_identifier_code(record_code);` |
| Timestamp về UTC | `etl_normalize_iso_datetime` | ISO 8601 + UTC | Nhận timestamp có offset/timezone và chuyển về UTC `Z`; không tự đoán timezone. | `2026-08-10T14:30:00+07:00` → `2026-08-10T07:30:00.000000Z` | `SELECT etl_normalize_iso_datetime(updated_at);` |
| Textual NULL | `etl_normalize_null_token` | Generic ingestion | Trim và đổi `null`, `N/A`, `[NULL]`, `undefined`... thành `NULL`. | `[NULL]` → `NULL` | `SELECT etl_normalize_null_token(raw_value);` |
| Chuẩn hóa phần trăm | `etl_normalize_percentage` | Numeric 0..100 | Bỏ `%`, chuẩn hóa Decimal và validate miền 0..100. | `25.50%` → `25.5` | `SELECT etl_normalize_percentage(ownership_pct);` |
| Chuẩn hóa tên người | `etl_normalize_person_name` | Unicode NFC + whitespace | Chuẩn hóa tên nhưng giữ case và không giả định thứ tự họ/tên theo quốc gia. | `  Nguyễn   Văn   An ` → `Nguyễn Văn An` | `SELECT etl_normalize_person_name(full_name);` |
| Chuẩn hóa xác suất/score | `etl_normalize_probability` | Numeric 0..1 | Chỉ nhận finite number trong miền 0..1. | `0.82` → `0.82` | `SELECT etl_normalize_probability(match_score);` |
| Kiểm tra có dữ liệu | `etl_quality_is_present` | Data quality | `TRUE` khi không phải `NULL`, blank hoặc null-token. | ` N/A ` → `FALSE` | `SELECT etl_quality_is_present(citizen_id);` |
| Kiểm tra số trong khoảng | `etl_quality_number_in_range` | Data quality / Decimal | Validate Decimal trong min/max inclusive. | `105`, min `0`, max `100` → `FALSE` | `SELECT etl_quality_number_in_range(score, '0', '100');` |
| Record ID ổn định | `etl_stable_record_id` | SHA-256 provenance key | Tạo ID deterministic từ `source` + `natural_key` cho idempotent load/dedup. | `tax-system`, `0101234567` → `SHA-256 64 ký tự` | `SELECT etl_stable_record_id(source_system, natural_key);` |
