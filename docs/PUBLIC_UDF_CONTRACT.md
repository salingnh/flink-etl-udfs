# Public UDF contract

## Category

`category` describes the ETL operation only. It must never describe a business domain,
country, protocol family, or standards body.

Allowed values:

| Category | Meaning |
| --- | --- |
| `conversion` | Normalize/canonicalize/convert a value |
| `validation` | Return validity/quality status |
| `classification` | Classify an input into a known type |
| `generation` | Build a derived deterministic key/value |
| `masking` | Redact or mask sensitive content |
| `fingerprint` | Build a digest/fingerprint |
| `extraction` | Extract one component from a value |
| `enrichment` | Obtain derived data through controlled external enrichment |

Named standards stay in the independent `standard` metadata field, for example
`ISO 2108`, `RFC 9562`, `W3C DID Core`, or `STIX 2.1`.

## Internal TRY_CAST input policy

Every public scalar UDF accepts arbitrary SQL scalar input types at the PyFlink
boundary. Public wrappers deliberately **do not declare `input_types`**.

The execution contract is:

```text
arbitrary SQL scalar value
        ↓
Python runtime value
        ↓
internal TRY_CAST to the transform's expected input type
        ↓
existing normalization / extraction / validation logic
        ↓
result
```

If an input cannot be converted to the expected type, or the converted value is
malformed for the transform, the UDF returns SQL `NULL` rather than failing the
Flink task.

Example for a transform whose logical input is STRING:

```text
VARCHAR '84912345678'  -> '84912345678'
BIGINT  84912345678    -> '84912345678'
BOOLEAN TRUE           -> 'true'
DATE 2026-08-15        -> '2026-08-15'
BYTES b'abc'            -> 'abc' when valid UTF-8
```

After conversion, the original transform semantics are unchanged. For example,
`VN_NORMALIZE_MOBILE_PHONE(BIGINT '84912345678')` first becomes the internal string
`'84912345678'`, then the existing Vietnam phone normalizer returns `0912345678`.
A BOOLEAN or DATE can be converted to STRING but is not a valid mobile number, so
the final result is `NULL`.

The shared implementation lives in `flink_etl_udfs.udfs._safe` and currently
supports internal targets `STRING`, `BOOLEAN`, `BIGINT`, `DOUBLE`, `DECIMAL`, `DATE`,
and `TIMESTAMP`.

## Error boundary

Data/conversion failures are fail-soft and return `NULL`. Infrastructure failures
are not data conversion failures. In particular, external enrichment must not hide
network/service outages as missing business data, so `OSError`/timeout-style
infrastructure failures are allowed to propagate to Flink retry/failure handling.

## Wrapper rule

Public UDF wrapper modules must use `try_udf(..., cast_types=[...])` and must not set
PyFlink `input_types=...`. CI enforces this rule for every module referenced by
`PUBLIC_FUNCTIONS` and the Flink 2.2.1 smoke test invokes the same UDF with VARCHAR,
BIGINT, BOOLEAN, and DATE inputs.
