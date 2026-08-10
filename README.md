# flink-etl-udfs

Curated **PyFlink UDF library for deterministic ETL normalization**. Project ưu tiên generic transforms và chuẩn phổ biến, không tạo UDF chỉ vì dataset có tên field khác nhau.

```text
Generic transform / standard
        ↓
Country/domain function khi thật sự cần
        ↓
Thin PyFlink UDF wrapper
        ↓
Flink SQL registry
```

## Version 0.5.0 — breaking cleanup

`0.5.0` giảm public SQL surface từ 104 xuống **67 UDF**. Không giữ backward compatibility alias.

Đã xóa các nhóm function dataset-specific, heuristic yếu hoặc phù hợp parser/reference-data layer hơn scalar UDF: alias education/Vietnam, custom OSINT vocabularies, scientific/insurance scalar packs, GTFS ID cleanup, telemetry-quality mapping và các helper chỉ uppercase/trim nhưng không có standard semantics rõ ràng.

## Documentation

- [`docs/FUNCTION_CATALOG.md`](docs/FUNCTION_CATALOG.md) — toàn bộ 67 SQL UDF với tên hiển thị tiếng Việt, phạm vi validation, trước → sau và SQL example.
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
| `osint_*` | Chỉ observation/account-handle semantics |
| `vn_*` | Chỉ CMND/CCCD và MST Việt Nam |
| `finance_*` | IBAN, BIC, ISO 20022, LEI |
| `health_*` | FHIR, HL7 v2, DICOM UID |
| `supply_*` | GS1 GTIN, SSCC, EPCIS |
| `iot_*` | OPC UA NodeId, DLMS/COSEM OBIS |
| `geo_*` | Latitude, longitude, EPSG code |

## Ví dụ dân cư / thuế

```sql
SELECT
    etl_normalize_person_name(full_name)              AS full_name_norm,
    etl_normalize_e164(phone, '+84')                  AS phone_e164,
    etl_normalize_address_text(address)               AS address_norm,
    vn_normalize_citizen_id(citizen_id)               AS citizen_id_norm,
    vn_normalize_tax_id(tax_id)                       AS tax_id_norm,
    vn_classify_tax_id_structure(tax_id)              AS tax_id_structure
FROM citizen_tax_source;
```

```text
"  Nguyễn   Văn An "        → "Nguyễn Văn An"
"0912 345 678"              → "+84912345678"
"12 Nguyễn Trãi,   Hà Nội"  → "12 Nguyễn Trãi, Hà Nội"
"034 190 006 609"           → "034190006609"
"0101234567001"             → "0101234567-001"
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

Custom Python environment có PyFlink 2.3.0:

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
  --pyFiles dist/flink_etl_udfs-0.5.0-py3-none-any.whl \
  --pyRequirements requirements.txt
```

## Engineering rules

- Preserve `NULL` theo mặc định.
- Không gọi network/database/API từ scalar UDF.
- Dùng Decimal semantics cho tiền, thuế và phí.
- Search/blocking key không phải canonical identity.
- Chỉ tạo country/domain UDF khi semantics thực sự khác generic layer.
- Danh mục thay đổi theo thời gian phải dùng reference data, không hard-code vào UDF.
- File/schema/protocol nặng như DICOM files, FHIR profiles, ACORD XML, NetCDF/GRIB, FITS/WCS, VCF/BCF/BAM, GTFS feed validation... phải dùng parser/validator chuyên dụng trước hoặc song song với Flink SQL.

## License

Apache-2.0.
