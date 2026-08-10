# Hàm OSINT

Đăng ký bằng `register_osint_udfs(t_env)`.

Sau cleanup, pack OSINT chỉ giữ các transform có semantics thật sự gắn với observation/tài khoản nguồn mở. Domain, URL, ASN, CVE, hash, LEI và Git ID đã chuyển sang các pack generic tương ứng.

| Tên hiển thị | SQL function | Phạm vi | Mô tả | Giá trị trước → sau | Ví dụ SQL |
| --- | --- | --- | --- | --- | --- |
| Tạo ID observation ổn định | `osint_build_observation_id` | SHA-256 provenance key | Hash `source_url + entity_key + observed_at` để dedup/history observation. | `https://example.gov.vn/a`, `org:0101234567`, `2026-08-10T07:30:00Z` → `SHA-256 64 ký tự` | `SELECT osint_build_observation_id(source_url, entity_key, observed_at);` |
| Chuẩn hóa username | `osint_normalize_username` | Public account handle | Trim, Unicode NFC và bỏ `@` đầu; giữ case vì semantics phụ thuộc nền tảng. | ` @@User.Name ` → `User.Name` | `SELECT osint_normalize_username(username);` |

Các dữ liệu OSINT còn lại dùng generic packs: `net_*` cho domain/URL/DNS/ASN/MIME, `security_*`/`cti_*` cho IOC/CTI, `code_*` cho Git, `finance_normalize_lei` cho LEI, `etl_normalize_probability` cho confidence và `etl_normalize_iso_datetime` cho thời gian quan sát.
