# Hàm đặc thù Việt Nam: dân cư và thuế

Đăng ký bằng `register_vietnam_udfs(t_env)`.

Pack `vn_*` chỉ còn quy tắc thật sự phụ thuộc cấu trúc định danh Việt Nam. Tên người, địa chỉ, số điện thoại, mã trường/học sinh/giáo viên và các cleanup chung phải dùng `etl_*` generic functions.

| Tên hiển thị | SQL function | Phạm vi | Mô tả | Giá trị trước → sau | Ví dụ SQL |
| --- | --- | --- | --- | --- | --- |
| Phân loại CMND / CCCD | `vn_classify_identity_id` | Việt Nam, structural | Phân loại ID 9 chữ số thành `cmnd_9`, 12 chữ số thành `cccd_12`; không xác minh giấy tờ có hiệu lực. | `034190006609` → `cccd_12` | `SELECT vn_classify_identity_id(identity_no);` |
| Phân loại cấu trúc MST | `vn_classify_tax_id_structure` | Việt Nam, structural | Trả `base_10` hoặc `extended_13`, chỉ mô tả hình thức identifier. | `0101234567-001` → `extended_13` | `SELECT vn_classify_tax_id_structure(tax_id);` |
| Chuẩn hóa CMND / CCCD | `vn_normalize_citizen_id` | Việt Nam, structural | Chỉ giữ ASCII digits và chấp nhận 9/12 chữ số; giữ leading zero. | `034 190 006 609` → `034190006609` | `SELECT vn_normalize_citizen_id(citizen_id);` |
| Chuẩn hóa mã số thuế | `vn_normalize_tax_id` | Việt Nam, structural | Chuẩn hóa về `10digits` hoặc `10digits-3digits`; registry validity phải lookup nguồn thuế có thẩm quyền. | `0101234567001` → `0101234567-001` | `SELECT vn_normalize_tax_id(tax_id);` |

Ví dụ số điện thoại Việt Nam không cần UDF riêng nữa: `0912 345 678`, `+84` → `+84912345678` bằng `SELECT etl_normalize_e164(phone, '+84');`.
