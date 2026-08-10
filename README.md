# flink-etl-udfs

Thư viện **PyFlink UDF tái sử dụng cho ETL**: chuẩn hóa dữ liệu, masking, fingerprinting, data quality và canonicalization theo các chuẩn phổ biến.

Thiết kế của project ưu tiên:

```text
Generic cross-domain transform
        ↓
Domain / country profile khi thực sự cần
        ↓
Thin PyFlink UDF wrapper
        ↓
Flink SQL registry
```

Không tạo một UDF mới chỉ vì dataset có tên cột khác nhau. Ví dụ `ma_hoc_sinh`, `ma_giao_vien`, `customer_code`, `case_code` và `asset_code` có cùng data contract thì nên dùng chung `etl_normalize_identifier_code`.

## Documentation

- [`docs/FUNCTION_CATALOG.md`](docs/FUNCTION_CATALOG.md) — danh mục toàn bộ SQL UDF, tên hiển thị tiếng Việt, phạm vi validation, input → output và SQL example.
- [`docs/GENERICITY_REVIEW.md`](docs/GENERICITY_REVIEW.md) — rà soát function nào nên generic, function nào phải giữ domain-specific và hướng migration.
- [`docs/ETL_RESEARCH.md`](docs/ETL_RESEARCH.md) — research ETL theo lĩnh vực và ranh giới parser-vs-UDF.
- [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) — dependency và cách deploy Python UDF lên Flink cluster.

## Version 0.4.0 — generic-first API

Các P0 function generic mới:

| SQL function | Mục đích |
| --- | --- |
| `etl_normalize_person_name` | Unicode NFC + whitespace cho tên người, không giả định quốc gia |
| `etl_latin_name_search_key` | Search/blocking key không dấu cho tên Latin-script |
| `etl_normalize_identifier_code` | Chuẩn hóa mã nghiệp vụ dùng chung giữa nhiều dataset |
| `etl_normalize_account_identifier` | Cleanup mã account/reference chữ-số; không phải IBAN validator |
| `etl_normalize_address_text` | Tiền xử lý địa chỉ free-text trước parser/geocoder/reference lookup |

Các API `vn_normalize_name`, `vn_normalize_address`, `vn_normalize_school_code`, `vn_normalize_teacher_code`, `vn_normalize_student_code` và `vn_normalize_bank_account` vẫn tồn tại để backward compatibility nhưng code mới nên ưu tiên generic counterpart.

`vn_classify_tax_id` cũng được giữ cho job cũ. Pipeline mới nên dùng `vn_classify_tax_id_structure`, trả nhãn trung tính `base_10` / `extended_13` thay vì suy diễn loại hình pháp lý chỉ từ cấu trúc MST.

## Chuẩn được ưu tiên

Thư viện ưu tiên canonical form và chuẩn trao đổi dữ liệu phổ biến: Unicode NFC, ISO 8601, ITU-T E.164, ISO 4217, ISO 13616/IBAN, ISO 9362/BIC, ISO 17442/LEI, ISO 20022, GS1 GTIN/SSCC/EPCIS, STIX/MITRE ATT&CK, FHIR/HL7/DICOM, OPC UA, DLMS/COSEM, GTFS và EPSG.

Một scalar UDF chỉ nên thực hiện canonicalization, syntax validation hoặc checksum khi phù hợp. Danh mục thay đổi theo thời gian — ví dụ mã hành chính, ISO currency list, BIC directory, FHIR ValueSet, EPSG registry, CVE/ATT&CK metadata — nên nằm ở reference-data/enrichment layer thay vì hard-code vào UDF.

## Install

Development:

```bash
python -m pip install -r requirements-dev.txt
python -m pip install -e . --no-deps
pytest
```

Custom Python environment có PyFlink 2.3.0:

```bash
python -m pip install -r requirements-flink.txt
python -m pip install -r requirements.txt
python -m pip install . --no-deps
```

## Register UDF

Chỉ đăng ký pack mà job cần:

```python
from pyflink.table import EnvironmentSettings, TableEnvironment
from flink_etl_udfs.registry import register_common_udfs, register_vietnam_udfs

settings = EnvironmentSettings.in_streaming_mode()
t_env = TableEnvironment.create(settings)

register_common_udfs(t_env)
register_vietnam_udfs(t_env)
```

Ví dụ dữ liệu dân cư / thuế nhưng vẫn dùng generic transform khi có thể:

```sql
SELECT
    etl_normalize_person_name(full_name)                         AS full_name_norm,
    etl_normalize_e164(phone, '+84')                             AS phone_e164,
    etl_normalize_address_text(address)                          AS address_norm,
    vn_normalize_citizen_id(citizen_id)                          AS citizen_id_norm,
    vn_normalize_tax_id(tax_id)                                  AS tax_id_norm,
    vn_classify_tax_id_structure(tax_id)                         AS tax_id_structure,
    etl_normalize_identifier_code(source_record_code)            AS record_code_norm
FROM citizen_tax_source;
```

Ví dụ input/output tương ứng:

```text
"  Nguyễn   Văn An "        → "Nguyễn Văn An"
"0912 345 678"              → "+84912345678"
"12 Nguyễn Trãi,   Hà Nội"  → "12 Nguyễn Trãi, Hà Nội"
"034 190 006 609"           → "034190006609"
"0101234567001"             → "0101234567-001"
"0101234567-001"            → "extended_13"
" hs- 2026 / 001 "          → "HS-2026/001"
```

## Pure function trước, PyFlink wrapper sau

Business logic nằm ở `src/flink_etl_udfs/core/`:

```python
def normalize_value(value):
    ...
```

PyFlink wrapper chỉ khai báo type/determinism:

```python
normalize = udf(
    normalize_value,
    input_types=["STRING"],
    result_type="STRING",
    deterministic=True,
)
```

Cách này giúp cùng transform có thể tái sử dụng trong PyFlink, DuckDB/Python ingestion, Kafka producer, batch repair hoặc data-quality pipeline.

## Deploy lên Flink cluster

Build wheel:

```bash
python -m build
```

Submit ví dụ:

```bash
./bin/flink run \
  --python your_job.py \
  --pyFiles dist/flink_etl_udfs-0.4.0-py3-none-any.whl \
  --pyRequirements requirements.txt
```

`requirements.txt` chỉ chứa third-party package thực sự cần trên Python worker. `apache-flink` được tách sang `requirements-flink.txt` để tránh vô tình cài lại PyFlink cho từng worker/job.

## Parser / enrichment không nên nhét vào scalar UDF

Các format hoặc tác vụ cần file/network/schema-aware processing nên chạy trước hoặc song song với Flink SQL, ví dụ STIX validator, FHIR profile validator, HL7 parser, DICOM parser, ISO 20022 XML/XSD, EPCIS parser, OPC UA/DLMS client, GTFS feed validator, GDAL/PROJ, HTSlib/pysam, xarray/cfgrib, Astropy hoặc ACORD XML validator.

Sau parser/enrichment, record canonical có thể được đẩy vào Kafka/Avro/Parquet rồi dùng thư viện này cho row-level deterministic normalization.

## Engineering rules

- Preserve `NULL` theo mặc định.
- Invalid/unsupported row nên trả `NULL` hoặc quality flag thay vì làm fail toàn job nếu semantics cho phép.
- Không gọi network/database/API từ scalar UDF.
- Dùng Decimal semantics cho tiền, thuế, phí.
- Giữ raw value và canonical value riêng nếu transform có thể lossy.
- Không log plaintext PII.
- Search/blocking key không phải canonical identity.
- Country/domain rule chỉ nằm trong module riêng khi thật sự phụ thuộc country/domain.

## License

Apache-2.0.
