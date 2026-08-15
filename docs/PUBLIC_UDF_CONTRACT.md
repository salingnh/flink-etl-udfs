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

## Normalization semantics

Public normalizers follow the project-wide [ETL normalization philosophy](NORMALIZATION_PHILOSOPHY.md):

```text
arbitrary input
    -> internal TRY_CAST
    -> deterministic TRY_PARSE of supported representations
    -> semantic validation
    -> canonical output
    -> NULL when invalid, unsupported, or ambiguous
```

`normalize_*` therefore means **canonicalize supported source representations**, not
"accept only values that are already in the canonical lexical form". A named standard
usually defines the canonical output/semantic target. It does not require source data
to already be written exactly in that standard's preferred representation.

Normalizers must not guess ambiguous values. When multiple interpretations are
plausible and there is no explicit parameter that resolves the ambiguity, return
`NULL`.

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
normalization / extraction / validation logic
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

After conversion, transform-specific TRY_PARSE/canonicalization semantics are applied.
For example, a date normalizer can accept the internal string `15/08/2026` and emit
`2026-08-15` when that representation is unambiguous. An invalid date such as
`31/02/2026` returns `NULL`.

The shared input-cast implementation lives in `flink_etl_udfs.udfs._safe` and currently
supports internal targets `STRING`, `BOOLEAN`, `BIGINT`, `DOUBLE`, `DECIMAL`, `DATE`,
and `TIMESTAMP`.

## Sample-driven metadata contract

Every public normalizer must maintain executable input→output sample cases. The exact
same cases are used by unit tests and by the Elasticsearch metadata exporter. A code
change that adds a supported representation must therefore update the executable sample
contract first; generated metadata descriptions inherit the tested examples instead of
maintaining a second prose-only copy.

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
