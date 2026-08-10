# Hàm cho dữ liệu Việt Nam: dân cư, thuế, giáo dục, ngân hàng

Đăng ký bằng `register_vietnam_udfs(t_env)`.

Nhóm `vn_*` chỉ nên chứa quy tắc thật sự phụ thuộc Việt Nam. Một số tên cũ vẫn được giữ để tương thích với job hiện tại nhưng implementation đã delegate sang generic `etl_*`; code mới nên ưu tiên generic counterpart được ghi trong cột **Khuyến nghị**.

| Tên hiển thị | SQL function | Phạm vi | Mô tả | Giá trị trước → sau | Ví dụ SQL | Khuyến nghị |
| --- | --- | --- | --- | --- | --- | --- |
| Tạo khóa blocking công dân/khách hàng | `vn_build_entity_blocking_key` | Entity resolution profile Việt Nam | Ghép search key của tên, điện thoại `+84` và email thành blocking key dễ đọc để tạo candidate. Không khẳng định hai bản ghi là cùng người. | `Nguyễn Văn A`, `0912345678`, `USER@EXAMPLE.COM` → `n=nguyen van a\|p=+84912345678\|e=user@example.com` | `SELECT vn_build_entity_blocking_key(full_name, phone, email);` | Giữ `vn_*` vì phone profile dùng `+84`. |
| Phân loại CMND / CCCD | `vn_classify_identity_id` | Việt Nam, structural | Phân loại ID 9 chữ số thành `cmnd_9`, 12 chữ số thành `cccd_12`. Chỉ dựa trên cấu trúc/độ dài. | `034190006609` → `cccd_12` | `SELECT vn_classify_identity_id(identity_no);` | Giữ domain-specific. |
| Phân loại MST chính / đơn vị phụ thuộc | `vn_classify_tax_id` | Việt Nam, structural | Sau khi normalize MST, trả `enterprise` cho 10 số hoặc `dependent_unit` cho dạng `10 số-3 số`. | `0101234567-001` → `dependent_unit` | `SELECT vn_classify_tax_id(tax_id);` | Giữ domain-specific. |
| Chuẩn hóa năm học | `vn_normalize_academic_year` | Education profile | Chuẩn hóa năm học hai năm liên tiếp. Không phải ISO date. | `2025/26` → `2025-2026` | `SELECT vn_normalize_academic_year(academic_year);` | Giữ education profile. |
| Chuẩn hóa địa chỉ Việt Nam dạng text | `vn_normalize_address` | Compatibility alias | Chuẩn hóa Unicode, whitespace và dấu phân cách; không parse tỉnh/huyện/xã. | `12 Nguyễn Trãi,   P. Bến Thành` → `12 Nguyễn Trãi, P. Bến Thành` | `SELECT vn_normalize_address(address);` | **Ưu tiên `etl_normalize_address_text`.** |
| Chuẩn hóa mã tài khoản dạng chữ-số | `vn_normalize_bank_account` | Compatibility alias | Bỏ separator phổ biến và uppercase mã tài khoản/reference. Không xác minh tài khoản tồn tại và không phải IBAN validator. | `001-234.567 890` → `001234567890` | `SELECT vn_normalize_bank_account(account_no);` | **Ưu tiên `etl_normalize_account_identifier`.** |
| Chuẩn hóa CMND / CCCD | `vn_normalize_citizen_id` | Việt Nam, structural | Chỉ giữ ASCII digits và chấp nhận cấu trúc 9 hoặc 12 chữ số; giữ leading zero. Không kiểm tra giấy tờ có tồn tại/hiệu lực. | `034 190 006 609` → `034190006609` | `SELECT vn_normalize_citizen_id(citizen_id);` | Giữ domain-specific. |
| Chuẩn hóa họ tên | `vn_normalize_name` | Compatibility alias | NFC + chuẩn hóa whitespace, giữ nguyên case. Logic không phụ thuộc Việt Nam. | `  Nguyễn   Thị Ngân ` → `Nguyễn Thị Ngân` | `SELECT vn_normalize_name(full_name);` | **Ưu tiên `etl_normalize_person_name`.** |
| Chuẩn hóa số điện thoại Việt Nam | `vn_normalize_phone` | ITU-T E.164 profile `+84` | Convenience wrapper của E.164 với default country code Việt Nam. | `0983 132 288` → `+84983132288` | `SELECT vn_normalize_phone(phone);` | Với pipeline đa quốc gia dùng `etl_normalize_e164(phone, country_code)`. |
| Chuẩn hóa mã trường | `vn_normalize_school_code` | Compatibility alias | Remove whitespace, uppercase và kiểm tra syntax mã nghiệp vụ. Không lookup danh mục trường. | ` thpt- 001 ` → `THPT-001` | `SELECT vn_normalize_school_code(school_code);` | **Ưu tiên `etl_normalize_identifier_code`.** |
| Chuẩn hóa SMS brand name | `vn_normalize_sms_brandname` | Telecom profile / syntax cleanup | Remove whitespace và uppercase sender brand label. Không kiểm tra brand name đã được operator cấp hay không. | `  vnpt ca ` → `VNPTCA` | `SELECT vn_normalize_sms_brandname(sender_id);` | Giữ profile; registry/operator validation phải ở lookup layer. |
| Chuẩn hóa mã học sinh | `vn_normalize_student_code` | Compatibility alias | Cùng logic generic identifier-code; không phụ thuộc một hệ thống giáo dục cụ thể. | ` hs- 2026/001 ` → `HS-2026/001` | `SELECT vn_normalize_student_code(student_code);` | **Ưu tiên `etl_normalize_identifier_code`.** |
| Chuẩn hóa mã số thuế Việt Nam | `vn_normalize_tax_id` | Việt Nam, structural | Chuẩn hóa về `10digits` hoặc `10digits-3digits`. Chỉ kiểm tra cấu trúc; xác minh doanh nghiệp phải dùng registry/reference data có thẩm quyền. | `0101234567001` → `0101234567-001` | `SELECT vn_normalize_tax_id(tax_id);` | Giữ domain-specific. |
| Chuẩn hóa mã giáo viên | `vn_normalize_teacher_code` | Compatibility alias | Cùng logic generic identifier-code; không phụ thuộc dataset giáo viên cụ thể. | ` gv- 2026/001 ` → `GV-2026/001` | `SELECT vn_normalize_teacher_code(teacher_code);` | **Ưu tiên `etl_normalize_identifier_code`.** |
| Khóa tìm kiếm tên tiếng Việt | `vn_name_search_key` | Compatibility alias / Latin-script blocking | Bỏ dấu, lowercase và tokenize để search/blocking. Không dùng làm ID canonical. | `Đặng Thị Hồng` → `dang thi hong` | `SELECT vn_name_search_key(full_name);` | **Ưu tiên `etl_latin_name_search_key`.** |

## Ví dụ migration từ dataset-specific sang generic

Thay vì:

```sql
SELECT
    vn_normalize_school_code(ma_truong),
    vn_normalize_teacher_code(ma_giao_vien),
    vn_normalize_student_code(ma_hoc_sinh)
FROM education_source;
```

nên dùng:

```sql
SELECT
    etl_normalize_identifier_code(ma_truong),
    etl_normalize_identifier_code(ma_giao_vien),
    etl_normalize_identifier_code(ma_hoc_sinh)
FROM education_source;
```

Cùng function đó có thể tái sử dụng cho `customer_code`, `case_code`, `asset_code`, `policy_code` hoặc bất kỳ mã nghiệp vụ nào có cùng data contract.
