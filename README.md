# flink-etl-udfs

Curated PyFlink UDF library for deterministic ETL normalization and controlled enrichment.

## Version 0.7.0 — standard-first public API

Public SQL names now follow:

```text
<standard>_<operation>_<subject>
```

Examples:

```text
iso8601_normalize_datetime_utc
iso13616_normalize_iban
iso2108_normalize_isbn13
iso3166_normalize_alpha3
rfc3986_normalize_uri
rfc9562_normalize_uuid
w3c_did_normalize
stix21_normalize_id
gs1_normalize_gtin
```

When no single external standard owns the semantics, the name uses a precise generic namespace such as `etl_*`, `url_*`, `dns_*`, `ip_*`, `hash_*`, `osint_*` or `vn_*`.

`0.7.0` is intentionally breaking: legacy SQL names and `registry.py` were removed instead of keeping aliases.

## Public API

The source of truth for SQL name, display name and Python entrypoint is:

```python
from flink_etl_udfs.public_api import PUBLIC_FUNCTIONS
```

See [`docs/FUNCTION_CATALOG.md`](docs/FUNCTION_CATALOG.md) for the complete **66-function** public surface.

## New standards added from the identity/identifier catalog

- ICAO Doc 9303 travel-document key
- ISO/IEC 18013-1 driving-licence key
- ISO/IEC 18013-5 mDL key
- ISO/IEC 23220 mobile eID/mdoc key
- ISO 3166-1 alpha-2/alpha-3 → alpha-3 normalization
- OpenID Connect `iss + sub` subject key
- W3C ActivityStreams 2.0 object IRI
- RFC 3986 URI normalization
- ISO 26324 DOI
- ISO 3297 ISSN
- ISO 2108 ISBN-13
- W3C DID Core
- RFC 9562 UUID
- RFC 8141 URN

Existing domain-prefixed standard functions were renamed to their standards, for example `finance_normalize_iban → iso13616_normalize_iban` and `security_normalize_cve → cve_normalize_id`.

## SQL Gateway deployment

Build a self-contained `python.files` ZIP. The normal CLI build vendors `requirements.txt` reference-data dependencies into the archive:

```bash
python scripts/build_python_files_zip.py
```

Upload `dist/flink_etl_udfs.zip`, then register only the UDFs required by the SQL session:

```sql
SET 'python.files' = 's3://fusion_center/transform-library/flink_etl_udfs.zip';

CREATE TEMPORARY SYSTEM FUNCTION ISO2108_NORMALIZE_ISBN13
AS 'flink_etl_udfs.udfs.standards.iso2108_normalize_isbn13'
LANGUAGE PYTHON;

CREATE TEMPORARY SYSTEM FUNCTION ISO3166_NORMALIZE_ALPHA3
AS 'flink_etl_udfs.udfs.standards.iso3166_normalize_alpha3'
LANGUAGE PYTHON;

SELECT
    ISO2108_NORMALIZE_ISBN13('0-306-40615-2') AS isbn13,
    ISO3166_NORMALIZE_ALPHA3('VN') AS country_alpha3;
```

See [`examples/sql_gateway.sql`](examples/sql_gateway.sql).

## Vietnam-specific functions

Country-specific logic remains under `vn_*` only when the semantics genuinely differ from a generic/international standard:

```sql
SELECT
    VN_NORMALIZE_MOBILE_PHONE(phone) AS phone_vn,
    VN_NORMALIZE_CITIZEN_ID(citizen_id) AS citizen_id,
    VN_NORMALIZE_TAX_ID(tax_id) AS tax_id
FROM source_table;
```

The mobile normalizer includes the closed 2018 migration from legacy 11-digit Vietnamese mobile prefixes to current 10-digit prefixes.

## Generic functions retained

The cleanup keeps reusable transforms such as address/name normalization, JSON canonicalization/flattening, email/IP normalization, masking/fingerprinting, URL/domain cleanup, stable record IDs and controlled profile enrichment.

Low-value public wrappers that are easy to express with built-in SQL or were excessively narrow were removed, including raw trim/whitespace/NFC wrappers, `digits_only`, generic range/probability wrappers, ASN/DNS-record/MIME wrappers, Git hash wrappers, OSINT username cleanup and latitude/longitude range wrappers.

## Dependencies

`pycountry==24.6.1` provides versioned ISO 3166 reference data while retaining Python 3.9 compatibility. PyFlink remains supplied by the Flink 2.2.1 runtime and is not installed from worker `requirements.txt`.

Development:

```bash
python -m pip install -r requirements-dev.txt
python -m pip install -e . --no-deps
pytest
```

## Engineering rules

- Prefer named standards over domain labels when a function implements a specific standard.
- Do not claim full standard compliance when a function performs only syntax/checksum normalization.
- Registry membership and mutable reference data must use maintained reference datasets.
- Keep external REST enrichment nondeterministic and bounded by timeout/capacity.
- Preserve raw values alongside normalized values when normalization may be lossy.

## License

Apache-2.0.
