# Rà soát genericity và standard-first cleanup

Version `0.7.0` tiếp tục nguyên tắc breaking cleanup: **không giữ compatibility alias**.

## Quy tắc giữ function

Một public UDF chỉ nên tồn tại khi có ít nhất một giá trị rõ ràng:

- canonicalization tái sử dụng cao;
- syntax/checksum/reference-data normalization theo chuẩn công khai;
- quy tắc quốc gia thực sự khác generic/international layer;
- provenance/masking/enrichment có semantics cụ thể và hữu ích.

Nếu logic chỉ là `trim`, `upper`, `lower`, collapse whitespace hoặc range check đơn giản, ưu tiên SQL built-in/internal helper thay vì public UDF riêng.

## Standard-first naming

Khi function gắn trực tiếp với một chuẩn, public name phải bắt đầu bằng namespace của chuẩn:

```text
iso8601_normalize_datetime_utc
iso13616_normalize_iban
iso17442_normalize_lei
iso2108_normalize_isbn13
rfc9562_normalize_uuid
w3c_did_normalize
stix21_normalize_id
gs1_normalize_gtin
```

Không dùng domain prefix như `finance_*`, `publication_*`, `health_*`, `security_*` nếu chuẩn đã cung cấp namespace chính xác hơn.

## Cleanup 0.7.0

Đã loại khỏi public SQL surface các wrapper quá mỏng hoặc quá hẹp:

- `digits_only`, `normalize_unicode_nfc`, `normalize_whitespace`, `null_if_blank`, `trim_text`;
- `etl_normalize_percentage`, `etl_normalize_probability`, `etl_quality_is_present`, `etl_quality_number_in_range`;
- ASN/DNS-record-type/MIME wrapper;
- Git object hash normalize/classify wrapper;
- OSINT username cleanup;
- latitude/longitude range wrapper.

Các implementation core có thể vẫn tồn tại nội bộ cho test/reuse nhưng không còn là public SQL contract.

## Country-specific layer

Giữ `vn_*` cho những semantics thật sự đặc thù Việt Nam: CMND/CCCD, cấu trúc MST và migration đầu số di động 11→10. Generic E.164 sử dụng public name `itu_e164_normalize_phone`.

## Reference data

Function như `iso3166_normalize_alpha3` phải kiểm tra/convert bằng reference data được duy trì, không được giả lập ISO compliance bằng regex. Lookup registry online hoặc danh mục thay đổi nhanh không nên hard-code vào từng scalar transform.
