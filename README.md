# flink-etl-udfs

Reusable PyFlink UDFs for ETL normalization, masking, fingerprinting, and data-quality preparation.

The project deliberately separates **pure transformations** from **PyFlink wrappers**. This keeps core logic fast to test, makes behavior reviewable, and avoids requiring a Flink runtime for every unit test.

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
  --pyFiles dist/flink_etl_udfs-0.1.0-py3-none-any.whl
```

Install third-party dependencies in the worker Python environment as well when a UDF needs them.

## Planned domains

Recommended next modules:

```text
core/
├── privacy.py
├── text.py
├── identifiers.py
├── datetime.py
├── money.py
├── network.py
├── url.py
├── json.py
├── vietnam/
│   ├── phone.py
│   ├── citizen_id.py
│   ├── tax_id.py
│   └── address.py
├── security/
│   ├── domain.py
│   ├── hash.py
│   └── ioc.py
└── quality/
    ├── validators.py
    └── flags.py
```

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
