# ETL normalization philosophy

This project treats normalization as an ETL conversion operation, not as a strict lexical validator.

## Core rule

A public normalizer should follow this flow:

```text
arbitrary SQL scalar input
        ↓
internal TRY_CAST to the transform's logical input type
        ↓
TRY_PARSE through an explicit, deterministic set of supported representations
        ↓
semantic validation
        ↓
one canonical output representation
        ↓
invalid / unsupported / ambiguous input -> SQL NULL
```

A named standard on a normalizer primarily defines the canonical output and semantic rules. The input does **not** need to already use that standard's canonical lexical form when the implementation can parse another common representation safely and deterministically.

Example:

```text
ISO8601_NORMALIZE_DATE("2026-08-15") -> "2026-08-15"
ISO8601_NORMALIZE_DATE("15/08/2026") -> "2026-08-15"
ISO8601_NORMALIZE_DATE("31/02/2026") -> NULL
```

The function canonicalizes to ISO 8601. It is not merely a test that the source string is already ISO 8601.

## Do not guess ambiguous data

TRY_PARSE must be deterministic. A normalizer may support many common representations, but it must not silently guess when two interpretations are both plausible.

For example, without an explicit date-order parameter:

```text
"15/08/2026" -> 2026-08-15   # unambiguous DMY because 15 cannot be a month
"2026/08/15" -> 2026-08-15   # explicit YMD
"01/02/2026" -> NULL         # DMY and MDY are both plausible
```

The same principle applies to locale-sensitive numbers, identifiers, phone numbers and other values. Prefer `NULL` over a plausible-but-unproven rewrite.

## Operation semantics

The public operation name/category must match the behavior:

| Operation | Contract |
| --- | --- |
| Normalize / canonicalize / conversion | Accept supported alternate representations and emit one canonical representation |
| Validate | Check whether input satisfies a rule and return validity/quality status |
| Classify | Map input to a known type/category without rewriting it into another identifier |
| Extract | Return a component already present in the input |
| Build / generation | Construct a new derived identifier/value from one or more components |
| Mask | Redact sensitive content |
| Fingerprint | Produce a deterministic digest/fingerprint |
| Enrich | Obtain derived information using a controlled external source/service |

A function named `normalize_*` should not behave like a validator unless no safe alternate representation exists. If the implementation only checks syntax, its documentation must say that explicitly.

## Standard-bound normalizers

When `standard` is present in metadata:

1. The description briefly explains what the standard is.
2. The description states the canonicalization scope implemented by the UDF.
3. It must not imply stronger validation than the code performs (for example registry membership when only syntax is checked).
4. Supported non-canonical input representations are allowed when the rewrite is deterministic.
5. Namespace- or provider-specific equivalence rules are not invented by a generic UDF.

## Sample-driven contract

Every public normalizer must have concrete sample cases. Those cases are executable contract data, not prose-only examples.

For each normalizer:

1. Add or change the normalization logic.
2. Add representative sample cases, including at least one alternate representation and one invalid/ambiguous case where meaningful.
3. Run the sample cases as unit tests against the pure transform implementation.
4. Use those exact same sample cases when generating the Elasticsearch metadata `description` examples.
5. Only after the function's samples pass should work move to the next normalizer.

This prevents documentation examples from drifting away from runtime behavior.

## Error behavior

Input conversion, parsing, format and semantic-validation failures are row-data failures and return SQL `NULL` under the public TRY_CAST contract.

Infrastructure errors are different. External enrichment/network failures must remain visible to Flink retry/failure handling and must not be converted into `NULL`, because that would make an outage indistinguishable from missing business data.
