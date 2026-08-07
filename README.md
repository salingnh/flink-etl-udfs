# flink-etl-udfs

Reusable PyFlink UDFs for ETL normalization, masking, fingerprinting, and data-quality preparation.

The project deliberately separates **pure transformations** from **PyFlink wrappers**. This keeps core logic fast to test, makes behavior reviewable, and avoids requiring a Flink runtime for every unit test.

## Documentation

- [`docs/ETL_RESEARCH.md`](docs/ETL_RESEARCH.md) — research matrix covering domains, data types, normalization strategy, open-source building blocks, implementation status, and parser-vs-UDF boundary.
- [`docs/FUNCTION_CATALOG.md`](docs/FUNCTION_CATALOG.md) — all registered SQL UDFs with signature, description, and example usage.

All public Python core functions include source-level docstrings. New functions should update the catalog and tests in the same change.

## Initial UDF catalog

| SQL function | Input | Output | Semantics |
|---|---|---|---|
| `sha256_fingerprint` | STRING | STRING | Deterministic SHA-256 fingerprint; preserves NULL |
| `mask_text` | STRING | STRING | Keeps first/last character, masks the middle |
| `mask_email` | STRING | STRING | Masks email local-part while preserving domain |
| `trim_text` | STRING | STRING | Trims leading/trailing whitespace |
| `normalize_whitespace` | STRING | STRING | Collapses whitespace runs to one ASCII space |
| `normalize_unicode_nfc` | STRING | STRING | Unicode NFC normalization |
| `null_if_blank` | STRING | STRING | Converts blank strings to NULL |
| `normalize_email` | STRING | STRING | Trims; lowercases domain only |
| `digits_only` | STRING | STRING | Retains ASCII digits only |
| `normalize_ip` | STRING | STRING | Canonical IPv4/IPv6 representation; invalid -> NULL |
| `normalize_cidr` | STRING | STRING | Canonical CIDR; clears host bits; invalid -> NULL |

## Install

Core-only development:

```bash
python -m pip install -e '.[test,dev]'
pytest
```

With PyFlink 2.3.0:

```bash
python -m pip install -e '.[flink]'
```

Apache Flink 2.3.0 is the stable target selected for the initial repository. Python UDF execution in current Flink documentation supports Python 3.9-3.12.

## Register all stable UDFs

```python
from pyflink.table import EnvironmentSettings, TableEnvironment
from flink_etl_udfs.registry import register_default_udfs

settings = EnvironmentSettings.in_streaming_mode()
t_env = TableEnvironment.create(settings)
register_default_udfs(t_env)
```

Then use them from SQL:

```sql
SELECT
  mask_text(phone),
  sha256_fingerprint(customer_id),
  normalize_email(email),
  normalize_ip(source_ip)
FROM source_table;
```

## Why pure functions + wrappers?

Avoid this pattern for every transform:

```python
@udf(...)
def normalize(...):
    # all business logic hidden inside Flink runtime wrapper
```

Prefer:

```python
def normalize_value(value):
    ...

normalize = udf(
    normalize_value,
    input_types=["STRING"],
    result_type="STRING",
    deterministic=True,
)
```

Benefits:

- Core behavior is testable without starting PyFlink.
- The same transformation can later be reused in DuckDB ingestion, Kafka producers, batch repair jobs, or data-quality tooling.
- Flink-specific concerns remain thin and explicit.
- Versioning semantic behavior becomes easier.

## Packaging for a Flink cluster

PyFlink supports attaching Python source, wheels, ZIP files, or directories with `--pyFiles`. A wheel built from this repository can therefore be distributed with the job or included in the Python environment used by the Flink workers.

Example:

```bash
python -m pip install build
python -m build

./bin/flink run \
  --python your_job.py \
  --pyFiles dist/flink_etl_udfs-0.3.0-py3-none-any.whl
```

Install third-party dependencies in the worker Python environment as well when a UDF needs them.

## Research roadmap domain packs

Version `0.3.0` expands the library from the generic + OSINT packs into the P0-P3 data types identified in the ETL research. Register only the packs a job needs, or use `register_all_udfs(t_env)` for exploration/testing.

```python
from flink_etl_udfs.registry import (
    register_all_udfs,
    register_common_udfs,
    register_finance_udfs,
    register_healthcare_udfs,
    register_industrial_udfs,
    register_insurance_udfs,
    register_scientific_udfs,
    register_security_standard_udfs,
    register_supply_chain_udfs,
    register_transport_geo_udfs,
    register_vietnam_udfs,
)
```

| Priority / domain | Representative SQL functions | Scope |
| --- | --- | --- |
| **P0 common** | `etl_normalize_iso_datetime`, `etl_normalize_date`, `etl_normalize_e164`, `etl_normalize_decimal`, `etl_normalize_currency_code`, `etl_canonicalize_json`, `etl_flatten_json`, `etl_is_valid_json`, `etl_quality_is_present`, `etl_quality_number_in_range`, `etl_stable_record_id` | Cross-domain normalization, data quality and provenance |
| **P1 Vietnam citizen** | `vn_normalize_citizen_id`, `vn_classify_identity_id`, `vn_normalize_tax_id`, `vn_classify_tax_id`, `vn_normalize_phone`, `vn_normalize_name`, `vn_name_search_key`, `vn_normalize_address` | Structural normalization; authoritative registry validation remains external |
| **P1 Education / operational** | `vn_normalize_school_code`, `vn_normalize_teacher_code`, `vn_normalize_student_code`, `vn_normalize_academic_year`, `vn_normalize_sms_brandname`, `vn_normalize_bank_account`, `vn_build_entity_blocking_key` | Education identifiers, SMS/log preparation, bank-account shape and entity-resolution blocking |
| **P2 STIX / CTI** | `cti_normalize_stix_type`, `cti_normalize_stix_id`, `cti_normalize_attack_technique_id` | Scalar identifier normalization; full STIX object/pattern validation belongs in a parser stage |
| **P2 Healthcare** | `health_normalize_fhir_id`, `health_normalize_fhir_reference`, `health_normalize_hl7_message_type`, `health_normalize_dicom_uid`, `health_normalize_dicom_modality` | FHIR/HL7/DICOM identifiers and metadata |
| **P2 Finance / ISO 20022** | `finance_normalize_iban`, `finance_normalize_bic`, `finance_normalize_iso20022_message_type` | IBAN mod-97, BIC/SWIFT shape and ISO 20022 message identifiers |
| **P2 Supply chain / EPCIS** | `supply_normalize_gtin`, `supply_normalize_sscc`, `supply_normalize_epcis_event_type` | GS1 check digits and EPCIS event names |
| **P2 Industrial / IoT** | `iot_normalize_opcua_node_id`, `iot_normalize_obis_code`, `iot_normalize_telemetry_quality` | OPC UA NodeId, DLMS/COSEM OBIS and telemetry quality |
| **P2 Transport / GIS** | `gtfs_normalize_id`, `geo_normalize_latitude`, `geo_normalize_longitude`, `geo_normalize_epsg_code` | GTFS identifiers and scalar spatial metadata |
| **P3 Genomics** | `genomics_normalize_chromosome`, `genomics_normalize_dna_sequence`, `genomics_normalize_vcf_genotype` | Chromosome, IUPAC DNA and VCF genotype scalar metadata |
| **P3 Climate** | `climate_normalize_cf_standard_name`, `climate_normalize_grib_short_name` | CF/NetCDF and GRIB metadata preparation |
| **P3 Astronomy** | `astro_normalize_fits_keyword`, `astro_normalize_celestial_frame` | FITS header keyword and celestial frame normalization |
| **P3 Insurance / ACORD** | `insurance_normalize_acord_version`, `insurance_normalize_policy_number`, `insurance_normalize_coverage_code` | ACORD-oriented metadata; full XML/XSD validation remains external |

### Why some researched formats are not fully parsed inside scalar UDFs

The following data types require file/network/schema-aware parsers and should run before or beside Flink SQL scalar normalization:

- STIX 2.x objects/patterns: `stix2` / OASIS validators.
- FHIR profiles and terminology: a FHIR validator/server such as HAPI FHIR or an equivalent validated pipeline.
- HL7 v2 ER7/MLLP: `hl7apy` or another HL7 parser.
- DICOM files/pixel metadata: `pydicom` or a DICOM-native ingestion service.
- ISO 20022 XML: schema-aware XML validation/parser.
- EPCIS JSON-LD/XML: GS1/EPCIS parser and schema validation.
- OPC UA and DLMS/COSEM protocol reads: protocol clients in source/enrichment operators, never a per-row scalar UDF.
- GTFS archives: feed-level validation before row ingestion.
- GeoTIFF/Shapefile/CRS transformation: GDAL/PROJ or a geospatial engine.
- BAM/CRAM/VCF/BCF: HTSlib/pysam/bcftools.
- NetCDF/GRIB: xarray/cfgrib/eccodes.
- FITS/WCS: Astropy.
- ACORD XML: licensed/authorized schemas plus XML/XSD validation.

These parser stages can emit normalized records into Kafka/Avro/Parquet, after which this library handles deterministic row-level cleanup in Flink.

## UDF engineering rules

- Preserve `NULL` by default.
- Mark a UDF deterministic only when repeated calls with the same arguments always produce the same result.
- Keep network/database/API calls out of normal scalar UDFs.
- Prefer `DECIMAL` semantics for money; do not introduce floating-point rounding into financial normalization.
- Keep raw and canonical values separate when normalization can be lossy.
- Avoid logging plaintext PII.
- Put country/domain-specific rules in separate modules instead of making generic functions guess.

## License

Apache-2.0.

## OSINT domain pack

The OSINT pack implements deterministic transforms for public-source observations while preserving the distinction between **observation**, **entity**, and **evidence**. It intentionally avoids claiming that a normalized username, email, phone, or search key proves identity ownership.

Register the pack separately from the common UDFs:

```python
from flink_etl_udfs.registry import register_osint_udfs

register_osint_udfs(t_env)
```

Example SQL:

```sql
SELECT
    osint_normalize_username(username) AS username_norm,
    osint_normalize_profile_url(profile_url) AS profile_url_norm,
    osint_normalize_domain(domain) AS domain_norm,
    osint_content_sha256(raw_evidence) AS evidence_hash,
    osint_normalize_observed_at_utc(observed_at) AS observed_at_utc,
    osint_normalize_confidence(confidence) AS confidence_norm,
    osint_normalize_verification_status(verification_status) AS verification_status_norm
FROM osint_source;
```

### OSINT function groups

| Group | Functions | Purpose |
| --- | --- | --- |
| Identity/account discovery | `osint_normalize_username`, `osint_normalize_platform`, `osint_normalize_name_search_key`, `osint_classify_account_identifier` | Normalize account handles and generate conservative search/blocking keys. |
| Web/profile evidence | `osint_canonicalize_url`, `osint_normalize_profile_url`, `osint_normalize_domain`, `osint_extract_url_host`, `osint_redact_url_secrets` | Canonicalize public URLs/domains and prevent accidental retention of URL credentials or secret query values. |
| Evidence/provenance | `osint_content_sha256`, `osint_build_observation_id`, `osint_normalize_observed_at_utc` | Build deterministic evidence hashes and observation identifiers with explicit timezone semantics. |
| Confidence/verification | `osint_normalize_confidence`, `osint_normalize_verification_status` | Validate confidence values and controlled verification states without inferring truth. |
| Security/IOC | `osint_normalize_hex_hash`, `osint_classify_hash_type`, `osint_normalize_cve` | Normalize common IOC digest and CVE representations. |
| Credential exposure | `osint_normalize_exposure_status` | Normalize remediation states for authorized credential-exposure datasets. |

The pack is intended for authorized ETL and analysis of public or legitimately obtained data. Complex collectors, identity attribution, sanctions matching, geolocation inference, and credential acquisition are deliberately outside the scalar-normalization layer.

Additional P1/P2 normalization functions:

- Internet infrastructure: `osint_normalize_asn`, `osint_normalize_dns_record_type`, `osint_normalize_mime_type`.
- Company/compliance graph: `osint_normalize_lei`, `osint_normalize_ownership_percentage`, `osint_normalize_entity_type`.
- Public source-code intelligence: `osint_normalize_repository_url`, `osint_normalize_git_object_id`, `osint_classify_git_object_hash`.

Network I/O and heavyweight enrichment are intentionally outside scalar UDFs. RDAP/DNS lookups, web crawling, EXIF parsing, sanctions/entity matching, geocoding, archive retrieval, and credential acquisition should run in dedicated enrichment stages with caching, rate-limit handling, provenance, and explicit access policy.
