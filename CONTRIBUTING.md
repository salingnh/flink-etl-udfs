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

## Python dependency requirements

If a change introduces a new third-party Python import under `src/`, the same change must declare how that package reaches the Flink runtime:

- `requirements.txt` — worker-side third-party libraries used by UDF/core code and suitable for `--pyRequirements`;
- `requirements-flink.txt` — the pinned `apache-flink` package for custom Python images/virtualenvs; keep it aligned with the cluster version;
- `requirements-dev.txt` — local test/lint/type-check/build tooling only.

Do not put `apache-flink` in the worker `requirements.txt` simply because wrappers import `pyflink`; a matching Flink distribution/custom runtime should provide PyFlink. Do not put heavy parser dependencies on every TaskManager when parsing happens in a separate ingestion service.

`tests/test_dependencies.py` scans source imports and intentionally fails when an unknown external import has no declared pip-provider mapping. When adding a dependency, update the test mapping and the appropriate requirements file together.

See `docs/DEPLOYMENT.md` for cluster, custom-image, and offline-install patterns.

## Documentation requirements

Every new public core transform must include a docstring that states:

- what the function normalizes or validates;
- whether validation is structural, checksum-based, or authoritative-reference based;
- important lossy behavior or semantic limits;
- expected invalid-input behavior (`None`/`False`).

Every new registered SQL UDF must also be documented under `docs/functions/` with its SQL name, signature, purpose, and a minimal usage example. Update `docs/FUNCTION_CATALOG.md` when the catalog structure or total coverage changes.

When adding a new domain, data type, standard, or open-source dependency, update the research material under `docs/ETL_RESEARCH.md` and `docs/research/` in the same change.

`tests/test_documentation.py` enforces two documentation contracts:

1. every public core transform has a source docstring;
2. every SQL UDF registered in `registry.py` appears in the function catalog.
