# Contributing

## Design rule

Every reusable transform should be split into two layers:

1. `flink_etl_udfs.core.*`: pure Python transformation, deterministic when possible, easy to unit-test.
2. `flink_etl_udfs.udfs.*`: thin PyFlink wrapper declaring Flink input/output types and determinism.

Do not put network/database calls inside scalar UDFs. Prefer lookup sources, async UDFs, broadcast/state patterns, or preprocessing for I/O-bound enrichment.

## Null and invalid-value policy

- Preserve `None` unless the function explicitly has a null-filling contract.
- Normalizers should not invent values.
- For invalid values, return `None` when the function contract is `value -> canonical value`; use separate validator/status functions when callers need error reasons.
- Never log plaintext sensitive values in UDF code.

## Adding a function

1. Add the pure transformation under `core/`.
2. Add unit tests including null, empty, invalid, Unicode, and boundary cases.
3. Add the thin PyFlink wrapper under `udfs/`.
4. Register it in `registry.py` only after its SQL name is considered stable.
5. Document semantic changes; avoid silently changing canonicalization behavior.
