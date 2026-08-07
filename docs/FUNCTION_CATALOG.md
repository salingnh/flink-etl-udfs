# Function Catalog

This catalog documents every SQL UDF registered by the repository. The implementation convention is **pure Python core transform → thin PyFlink wrapper → registry name**. Public core functions also contain source-code docstrings so IDE/tooling can expose the same semantics.

## General behavior

- Scalar normalizers preserve `NULL` and normally return `NULL` for malformed/unsupported input rather than raising per-record exceptions.
- Boolean quality functions return `FALSE` for missing/invalid input.
- Search/blocking keys are **candidate-generation features**, not canonical identity assertions.
- Functions validate syntax/shape unless the description explicitly mentions a checksum. Registry/reference-data validation must use an authoritative lookup/enrichment stage.
- Network/file I/O is deliberately excluded from scalar UDFs.

## Registration

```python
from flink_etl_udfs.registry import register_all_udfs

register_all_udfs(t_env)
```

For production jobs, prefer the narrowest domain registry instead of registering everything.

## Catalog files

- [Default + P0 common](functions/default-common.md)
- [OSINT](functions/osint.md)
- [Vietnam / citizen / education / banking](functions/vietnam.md)
- [Standards and specialized domains](functions/standards.md)

## Coverage

Documented SQL UDFs: **98**.

When adding a new UDF, update this catalog in the same change and add a public core-function docstring plus tests for valid, invalid, and `NULL` behavior.
