# Default and P0 Common Functions

## Default cross-domain helpers

Register with `register_default_udfs(t_env)`.

| SQL function | Signature | Description | Example |
| --- | --- | --- | --- |
| `digits_only` | `digits_only(value) → STRING` | Keep ASCII digits only; returns NULL when no digits remain. | `SELECT digits_only('+84 (912) 345-678');` |
| `mask_email` | `mask_email(email) → STRING` | Mask the local part of a simple email while retaining the domain. | `SELECT mask_email('alice@example.com');` |
| `mask_text` | `mask_text(value) → STRING` | Mask the middle of text while retaining boundary characters. | `SELECT mask_text('0912345678');` |
| `normalize_cidr` | `normalize_cidr(cidr) → STRING` | Canonicalize IPv4/IPv6 CIDR and clear host bits; invalid input becomes NULL. | `SELECT normalize_cidr('192.168.1.14/24');` |
| `normalize_email` | `normalize_email(email) → STRING` | Trim email and lowercase the domain only; malformed shape becomes NULL. | `SELECT normalize_email(' User.Name@EXAMPLE.COM ');` |
| `normalize_ip` | `normalize_ip(ip) → STRING` | Canonical compressed IPv4/IPv6 representation. | `SELECT normalize_ip('2001:0db8:0:0:0:0:0:1');` |
| `normalize_unicode_nfc` | `normalize_unicode_nfc(text) → STRING` | Apply Unicode NFC normalization without changing case. | `SELECT normalize_unicode_nfc(name);` |
| `normalize_whitespace` | `normalize_whitespace(text) → STRING` | Collapse Unicode whitespace runs to one space and trim. | `SELECT normalize_whitespace('  hello\n world  ');` |
| `null_if_blank` | `null_if_blank(text) → STRING` | Convert empty/whitespace-only strings to NULL. | `SELECT null_if_blank(raw_value);` |
| `sha256_fingerprint` | `sha256_fingerprint(value) → STRING` | Create a deterministic SHA-256 fingerprint for non-secret matching/deduplication. | `SELECT sha256_fingerprint(customer_id);` |
| `trim_text` | `trim_text(text) → STRING` | Trim leading and trailing whitespace while preserving NULL. | `SELECT trim_text(raw_name);` |

## P0 common ETL

Register with `register_common_udfs(t_env)`.

| SQL function | Signature | Description | Example |
| --- | --- | --- | --- |
| `etl_canonicalize_json` | `etl_canonicalize_json(json_text) → STRING` | Parse JSON and emit compact canonical JSON with sorted object keys. | `SELECT etl_canonicalize_json(payload);` |
| `etl_flatten_json` | `etl_flatten_json(json_text) → STRING` | Flatten nested JSON to dotted/indexed paths and return canonical JSON. | `SELECT etl_flatten_json(ocr_result);` |
| `etl_is_valid_json` | `etl_is_valid_json(json_text) → BOOLEAN` | Return whether a non-null input parses as JSON. | `SELECT etl_is_valid_json(payload);` |
| `etl_normalize_currency_code` | `etl_normalize_currency_code(code) → STRING` | Normalize a three-letter currency-code shape to uppercase. | `SELECT etl_normalize_currency_code('vnd');` |
| `etl_normalize_date` | `etl_normalize_date(date_text) → STRING` | Validate an ISO date and emit YYYY-MM-DD. | `SELECT etl_normalize_date('2026-08-07');` |
| `etl_normalize_decimal` | `etl_normalize_decimal(number_text) → STRING` | Normalize exact decimal text without binary floating-point rounding. | `SELECT etl_normalize_decimal('00123.4500');` |
| `etl_normalize_e164` | `etl_normalize_e164(phone, default_country_code) → STRING` | Conservatively normalize an international/national phone shape to E.164. | `SELECT etl_normalize_e164('0912345678', '+84');` |
| `etl_normalize_iso_datetime` | `etl_normalize_iso_datetime(timestamp) → STRING` | Normalize timezone-aware ISO-8601 timestamp to UTC Z; reject naive timestamps. | `SELECT etl_normalize_iso_datetime('2026-08-07T10:00:00+07:00');` |
| `etl_normalize_null_token` | `etl_normalize_null_token(value) → STRING` | Trim and convert common textual null markers such as null/N/A/[NULL] to NULL. | `SELECT etl_normalize_null_token('[NULL]');` |
| `etl_normalize_percentage` | `etl_normalize_percentage(value) → STRING` | Normalize exact percentage in inclusive 0..100 range. | `SELECT etl_normalize_percentage('25.50%');` |
| `etl_normalize_probability` | `etl_normalize_probability(value) → DOUBLE` | Parse finite probability in inclusive 0..1 range. | `SELECT etl_normalize_probability('0.82');` |
| `etl_quality_is_present` | `etl_quality_is_present(value) → BOOLEAN` | Check whether a value is not null/blank/common-null-token. | `SELECT etl_quality_is_present(customer_id);` |
| `etl_quality_number_in_range` | `etl_quality_number_in_range(value, min, max) → BOOLEAN` | Validate exact decimal text against optional inclusive bounds. | `SELECT etl_quality_number_in_range(score, '0', '100');` |
| `etl_stable_record_id` | `etl_stable_record_id(source, natural_key) → STRING` | Create deterministic SHA-256 record ID from provenance source and natural key. | `SELECT etl_stable_record_id('crm', customer_id);` |
