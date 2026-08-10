# Rà soát và cleanup tính generic

Version `0.5.0` thực hiện breaking cleanup: **không giữ compatibility alias**. Function chỉ được giữ khi có giá trị ETL rõ ràng, semantics đủ tổng quát hoặc bám một chuẩn/domain cụ thể.

## Tiêu chí giữ function

Một UDF được giữ khi đáp ứng ít nhất một trong các tiêu chí:

- canonicalization có hành vi rõ ràng và tái sử dụng cao;
- syntax/checksum theo chuẩn phổ biến;
- quy tắc quốc gia/domain thực sự khác generic layer;
- data-quality/provenance helper có semantics deterministic;
- không cần I/O, registry lookup hoặc parser file/network ở từng row.

## Đã xóa hoàn toàn

Các nhóm sau không còn core function, wrapper hay SQL alias legacy:

- `vn_normalize_name`, `vn_name_search_key`, `vn_normalize_address`;
- `vn_normalize_school_code`, `vn_normalize_teacher_code`, `vn_normalize_student_code`;
- `vn_normalize_bank_account`, `vn_normalize_phone`, `vn_normalize_academic_year`, `vn_normalize_sms_brandname`, `vn_build_entity_blocking_key`;
- `vn_classify_tax_id` với nhãn `enterprise/dependent_unit`;
- OSINT vocabulary/heuristic như account classification, platform, entity type, exposure status, verification status, profile URL, confidence, ownership percentage;
- scientific scalar helpers cho genomics/climate/astronomy;
- insurance/ACORD scalar helpers;
- telemetry-quality vocabulary, GTFS ID whitespace cleanup và DICOM modality uppercase helper.

## Thay bằng generic/standard function

| Logic cũ | Dùng function hiện tại |
| --- | --- |
| Tên người Việt Nam | `etl_normalize_person_name` |
| Search key tên Latin | `etl_latin_name_search_key` |
| Địa chỉ text | `etl_normalize_address_text` |
| Mã trường/học sinh/giáo viên/mã hồ sơ | `etl_normalize_identifier_code` |
| Điện thoại Việt Nam | `etl_normalize_e164(phone, '+84')` |
| Confidence score | `etl_normalize_probability` |
| Tỷ lệ sở hữu | `etl_normalize_percentage` |
| Observation timestamp | `etl_normalize_iso_datetime` |
| Domain / URL / ASN / DNS / MIME | `net_*` |
| Hash / CVE | `security_*` |
| Git repository/object ID | `code_*` |
| LEI | `finance_normalize_lei` |

## Các function Việt Nam còn lại

- `vn_normalize_citizen_id`
- `vn_classify_identity_id`
- `vn_normalize_tax_id`
- `vn_classify_tax_id_structure`

Đây là các function có cấu trúc identifier thật sự phụ thuộc quy ước Việt Nam. `vn_classify_tax_id_structure` chỉ trả `base_10` / `extended_13`, không suy diễn loại hình pháp lý.

## Các lĩnh vực được đưa ra khỏi scalar UDF

NetCDF/GRIB, FITS/WCS, BAM/CRAM/VCF/BCF, ACORD XML, GTFS feed validation, DICOM file parsing và các terminology/reference list thay đổi theo thời gian nên dùng parser/validator/reference-data layer chuyên dụng.

## Nguyên tắc tiếp theo

Nếu một function mới chỉ `trim + uppercase` nhưng không có data contract/standard riêng, ưu tiên dùng transform generic hoặc không tạo UDF mới. Nếu giá trị cần xác minh tồn tại trong registry, hãy join reference data thay vì hard-code danh mục vào Python scalar UDF.
