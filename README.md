# flink-etl-udfs

Curated **PyFlink UDF library for ETL normalization and controlled enrichment**. Project ưu tiên generic transforms và chuẩn phổ biến, không tạo UDF chỉ vì dataset có tên field khác nhau.

```text
Generic transform / standard
        ↓
Country/domain function khi thật sự cần
        ↓
Thin PyFlink UDF wrapper
        ↓
Flink SQL registry

External REST/API
        ↓
Synchronous enrichment client
        ↓
PyFlink scalar UDF (nondeterministic)
```

## Version 0.6.1

`0.6.1` có **69 public SQL UDF** và ưu tiên hai capability:

- `vn_normalize_mobile_phone`: chuẩn hóa số di động Việt Nam về dạng quốc gia 10 chữ số và chuyển các đầu số 11 số cũ của đợt đổi mã mạng năm 2018 sang đầu số mới.
- `enrich_extract_profile_url`: synchronous REST enrichment cho URL profile, gọi service `ExtractSource` và trả metadata profile dưới dạng JSON; wrapper dùng scalar UDF để tương thích Flink 2.2.1 SQL Gateway.

`0.6.0` bổ sung Vietnam mobile migration normalization và profile enrichment ban đầu.

`0.5.0` trước đó là breaking cleanup, giảm public SQL surface từ 104 xuống 67 UDF và loại toàn bộ compatibility alias.

## Documentation

- [`docs/FUNCTION_CATALOG.md`](docs/FUNCTION_CATALOG.md) — toàn bộ 69 SQL UDF với tên hiển thị tiếng Việt, phạm vi validation, trước → sau và SQL example.
- [`docs/GENERICITY_REVIEW.md`](docs/GENERICITY_REVIEW.md) — tiêu chí giữ/xóa function trong cleanup `0.5.0`.
- [`docs/ETL_RESEARCH.md`](docs/ETL_RESEARCH.md) — research ETL theo lĩnh vực và parser-vs-UDF boundary.
- [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) — dependency và cách deploy Python UDF lên Flink cluster.

## Domain packs hiện tại

```python
from flink_etl_udfs.registry import (
    register_all_udfs,
    register_code_udfs,
    register_common_udfs,
    register_default_udfs,
    register_enrichment_udfs,
    register_finance_udfs,
    register_geospatial_udfs,
    register_healthcare_udfs,
    register_industrial_udfs,
    register_internet_udfs,
    register_osint_udfs,
    register_security_udfs,
    register_supply_chain_udfs,
    register_vietnam_udfs,
)
```

Các prefix SQL chính:

| Prefix | Phạm vi |
| --- | --- |
| `etl_*` | Generic normalization, JSON, time, decimal, data quality, provenance |
| `net_*` | Domain, URL, DNS, ASN, MIME |
| `security_*` / `cti_*` | Hash, CVE, STIX, MITRE ATT&CK |
| `code_*` | Repository URL và Git object ID |
| `osint_*` | Deterministic observation/account-handle semantics |
| `enrich_*` | Controlled external REST/API enrichment |
| `vn_*` | CMND/CCCD, MST và quy tắc số di động đặc thù Việt Nam |
| `finance_*` | IBAN, BIC, ISO 20022, LEI |
| `health_*` | FHIR, HL7 v2, DICOM UID |
| `supply_*` | GS1 GTIN, SSCC, EPCIS |
| `iot_*` | OPC UA NodeId, DLMS/COSEM OBIS |
| `geo_*` | Latitude, longitude, EPSG code |

## Ví dụ dân cư / thuế

```sql
SELECT
    etl_normalize_person_name(full_name)              AS full_name_norm,
    vn_normalize_mobile_phone(phone)                  AS phone_vn,
    etl_normalize_e164(vn_normalize_mobile_phone(phone), '+84') AS phone_e164,
    etl_normalize_address_text(address)               AS address_norm,
    vn_normalize_citizen_id(citizen_id)               AS citizen_id_norm,
    vn_normalize_tax_id(tax_id)                       AS tax_id_norm,
    vn_classify_tax_id_structure(tax_id)              AS tax_id_structure
FROM citizen_tax_source;
```

```text
"  Nguyễn   Văn An "        → "Nguyễn Văn An"
"0169 123 4567"             → "0391234567"
"+84 912 345 678"           → "0912345678"
"12 Nguyễn Trãi,   Hà Nội"  → "12 Nguyễn Trãi, Hà Nội"
"034 190 006 609"           → "034190006609"
"0101234567001"             → "0101234567-001"
```

## Ví dụ profile enrichment

```sql
SELECT
    profile_url,
    enrich_extract_profile_url(profile_url) AS profile_source_json
FROM profile_source;
```

Endpoint mặc định có thể override trên TaskManager/Python worker:

```bash
export FLINK_ETL_PROFILE_EXTRACT_ENDPOINT='http://profile-service:31263/api/scrap-command/v1/Scrap/ExtractSource'
export FLINK_ETL_PROFILE_EXTRACT_TIMEOUT_SECONDS='10'
```

## Ví dụ internet / security

```sql
SELECT
    net_normalize_domain(domain),
    net_canonicalize_url(source_url),
    security_normalize_cve(cve_id),
    security_normalize_hex_hash(file_hash),
    cti_normalize_attack_technique_id(technique_id)
FROM security_source;
```

## Install

Development:

```bash
python -m pip install -r requirements-dev.txt
python -m pip install -e . --no-deps
pytest
```

Custom Python environment có PyFlink 2.2.1:

```bash
python -m pip install -r requirements-flink.txt
python -m pip install -r requirements.txt
python -m pip install . --no-deps
```

## Deploy

```bash
python -m build

./bin/flink run \
  --python your_job.py \
  --pyFiles dist/flink_etl_udfs-0.6.1-py3-none-any.whl \
  --pyRequirements requirements.txt
```

## Engineering rules

- Preserve `NULL` theo mặc định.
- Network/database/API trong scalar UDF phải có timeout rõ ràng, được khai báo `deterministic=False`, và chỉ dùng cho lookup/enrichment có latency/capacity đã kiểm soát. Với tải lớn, ưu tiên Async I/O/lookup service bên ngoài job SQL.
- Dùng Decimal semantics cho tiền, thuế và phí.
- Search/blocking key không phải canonical identity.
- Chỉ tạo country/domain UDF khi semantics thực sự khác generic layer.
- Danh mục thay đổi theo thời gian phải dùng reference data, không hard-code vào UDF; ngoại lệ là migration rule lịch sử đã đóng và có nguồn chuẩn như đổi đầu số di động năm 2018.
- File/schema/protocol nặng như DICOM files, FHIR profiles, ACORD XML, NetCDF/GRIB, FITS/WCS, VCF/BCF/BAM, GTFS feed validation... phải dùng parser/validator chuyên dụng trước hoặc song song với Flink SQL.

## License

Apache-2.0.
