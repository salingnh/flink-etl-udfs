# Hàm đặc thù Việt Nam: dân cư, thuế và số di động

Đăng ký bằng `register_vietnam_udfs(t_env)`.

Pack `vn_*` chỉ chứa quy tắc thật sự phụ thuộc Việt Nam: cấu trúc CMND/CCCD, mã số thuế và lịch sử chuyển đổi mã mạng di động. Tên người, địa chỉ và các cleanup chung vẫn dùng `etl_*` generic functions.

Các UDF Việt Nam được giữ self-contained trong module:

```text
flink_etl_udfs.udfs.vietnam
```

Mục tiêu là để SQL Gateway load một function Việt Nam mà không phải import toàn bộ `research_domains` và các domain không liên quan.

| Tên hiển thị | SQL function | Phạm vi | Mô tả | Giá trị trước → sau | Ví dụ SQL |
| --- | --- | --- | --- | --- | --- |
| Phân loại CMND / CCCD | `vn_classify_identity_id` | Việt Nam, structural | Phân loại ID 9 chữ số thành `cmnd_9`, 12 chữ số thành `cccd_12`; không xác minh giấy tờ có hiệu lực. | `034190006609` → `cccd_12` | `SELECT vn_classify_identity_id(identity_no);` |
| Phân loại cấu trúc MST | `vn_classify_tax_id_structure` | Việt Nam, structural | Trả `base_10` hoặc `extended_13`, chỉ mô tả hình thức identifier. | `0101234567-001` → `extended_13` | `SELECT vn_classify_tax_id_structure(tax_id);` |
| Chuẩn hóa CMND / CCCD | `vn_normalize_citizen_id` | Việt Nam, structural | Chỉ giữ ASCII digits và chấp nhận 9/12 chữ số; giữ leading zero. | `034 190 006 609` → `034190006609` | `SELECT vn_normalize_citizen_id(citizen_id);` |
| Chuẩn hóa số di động Việt Nam | `vn_normalize_mobile_phone` | Việt Nam, 2018 network-code migration | Chuẩn hóa `0...`, `84...`, `+84...`, `0084...` về số quốc gia 10 chữ số. Nếu input dùng đầu số 11 số cũ thì đổi sang mã mạng mới; chỉ kiểm tra structural mobile shape, không xác minh thuê bao đang active/nhà mạng hiện tại sau chuyển mạng giữ số. | `0169 123 4567` → `0391234567`; `+84 912 345 678` → `0912345678` | `SELECT vn_normalize_mobile_phone(phone);` |
| Chuẩn hóa mã số thuế | `vn_normalize_tax_id` | Việt Nam, structural | Chuẩn hóa về `10digits` hoặc `10digits-3digits`; registry validity phải lookup nguồn thuế có thẩm quyền. | `0101234567001` → `0101234567-001` | `SELECT vn_normalize_tax_id(tax_id);` |

## SQL Gateway entrypoint

```sql
SET 'python.files' = 's3://fusion_center/transform-library/flink_etl_udfs.zip';

CREATE TEMPORARY SYSTEM FUNCTION VN_NORMALIZE_MOBILE_PHONE
AS 'flink_etl_udfs.udfs.vietnam.normalize_vn_mobile_phone'
LANGUAGE PYTHON;
```

## Mapping đầu số 11 số cũ → 10 số

Mapping được encode theo đợt chuyển đổi mã mạng di động năm 2018:

- Viettel: `0162→032`, `0163→033`, `0164→034`, `0165→035`, `0166→036`, `0167→037`, `0168→038`, `0169→039`.
- VinaPhone: `0123→083`, `0124→084`, `0125→085`, `0127→081`, `0129→082`.
- MobiFone: `0120→070`, `0121→079`, `0122→077`, `0126→076`, `0128→078`.
- Vietnamobile: `0186→056`, `0188→058`.
- Gmobile/Gtel: `0199→059`.

Ví dụ:

```sql
SELECT
    phone_raw,
    vn_normalize_mobile_phone(phone_raw) AS phone_vn,
    etl_normalize_e164(vn_normalize_mobile_phone(phone_raw), '+84') AS phone_e164
FROM citizen_contact;
```

`vn_normalize_mobile_phone` cố ý trả dạng quốc gia `0xxxxxxxxx` để thể hiện rõ bước đổi đầu số 11→10. Khi cần khóa liên thông quốc tế, chain tiếp qua `etl_normalize_e164(..., '+84')`.
