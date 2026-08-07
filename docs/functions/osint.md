# OSINT Functions

## OSINT

Register with `register_osint_udfs(t_env)`.

| SQL function | Signature | Description | Example |
| --- | --- | --- | --- |
| `osint_build_observation_id` | `osint_build_observation_id(source_url, entity_key, observed_at) → STRING` | Create stable SHA-256 observation ID from source, entity key and observation time. | `SELECT osint_build_observation_id(source_url, entity_key, observed_at);` |
| `osint_canonicalize_url` | `osint_canonicalize_url(url) → STRING` | Canonicalize HTTP(S) URL, remove credentials/tracking parameters, sort query parameters. | `SELECT osint_canonicalize_url(raw_url);` |
| `osint_classify_account_identifier` | `osint_classify_account_identifier(value) → STRING` | Classify syntax conservatively as email, phone or username; not proof of ownership. | `SELECT osint_classify_account_identifier(handle);` |
| `osint_classify_git_object_hash` | `osint_classify_git_object_hash(hash) → STRING` | Classify a full Git object ID as sha1 or sha256. | `SELECT osint_classify_git_object_hash(commit_hash);` |
| `osint_classify_hash_type` | `osint_classify_hash_type(hash) → STRING` | Classify MD5/SHA1/SHA256/SHA512 by validated hex length. | `SELECT osint_classify_hash_type(file_hash);` |
| `osint_content_sha256` | `osint_content_sha256(content) → STRING` | SHA-256 hash arbitrary evidence content for deduplication/integrity. | `SELECT osint_content_sha256(raw_html);` |
| `osint_extract_url_host` | `osint_extract_url_host(url) → STRING` | Extract and normalize hostname from a valid HTTP(S) URL. | `SELECT osint_extract_url_host(profile_url);` |
| `osint_normalize_asn` | `osint_normalize_asn(asn) → STRING` | Normalize a 32-bit ASN to AS<number>. | `SELECT osint_normalize_asn('as13335');` |
| `osint_normalize_confidence` | `osint_normalize_confidence(value) → DOUBLE` | Parse finite confidence score in inclusive 0..1 range. | `SELECT osint_normalize_confidence('0.82');` |
| `osint_normalize_cve` | `osint_normalize_cve(value) → STRING` | Normalize CVE identifier to CVE-YYYY-NNNN... form. | `SELECT osint_normalize_cve('cve 2024 12345');` |
| `osint_normalize_dns_record_type` | `osint_normalize_dns_record_type(value) → STRING` | Normalize supported DNS resource-record type to uppercase. | `SELECT osint_normalize_dns_record_type('aaaa');` |
| `osint_normalize_domain` | `osint_normalize_domain(domain) → STRING` | Normalize DNS name to lowercase IDNA ASCII form. | `SELECT osint_normalize_domain('BÜCHER.DE.');` |
| `osint_normalize_entity_type` | `osint_normalize_entity_type(value) → STRING` | Map common graph entity aliases to controlled types such as person/organization/domain. | `SELECT osint_normalize_entity_type('company');` |
| `osint_normalize_exposure_status` | `osint_normalize_exposure_status(value) → STRING` | Normalize credential-exposure remediation state to open/remediated/suppressed/unknown. | `SELECT osint_normalize_exposure_status(status);` |
| `osint_normalize_git_object_id` | `osint_normalize_git_object_id(value) → STRING` | Normalize full 40-char SHA-1 or 64-char SHA-256 Git object ID; reject abbreviated IDs. | `SELECT osint_normalize_git_object_id(commit_hash);` |
| `osint_normalize_hex_hash` | `osint_normalize_hex_hash(value) → STRING` | Normalize known-length hexadecimal digest to lowercase. | `SELECT osint_normalize_hex_hash(file_hash);` |
| `osint_normalize_lei` | `osint_normalize_lei(value) → STRING` | Normalize and validate 20-character LEI using ISO 17442 mod-97. | `SELECT osint_normalize_lei(lei);` |
| `osint_normalize_mime_type` | `osint_normalize_mime_type(value) → STRING` | Normalize MIME media type to lowercase and drop optional parameters. | `SELECT osint_normalize_mime_type('Text/HTML; charset=UTF-8');` |
| `osint_normalize_name_search_key` | `osint_normalize_name_search_key(name) → STRING` | Build accent/punctuation-insensitive candidate-search key; never use as canonical identity. | `SELECT osint_normalize_name_search_key(display_name);` |
| `osint_normalize_observed_at_utc` | `osint_normalize_observed_at_utc(timestamp) → STRING` | Normalize timezone-aware observation timestamp to UTC Z. | `SELECT osint_normalize_observed_at_utc(observed_at);` |
| `osint_normalize_ownership_percentage` | `osint_normalize_ownership_percentage(value) → DOUBLE` | Parse ownership percentage in inclusive 0..100 range. | `SELECT osint_normalize_ownership_percentage('25.5%');` |
| `osint_normalize_platform` | `osint_normalize_platform(value) → STRING` | Normalize platform/domain label to compact lowercase representation. | `SELECT osint_normalize_platform('WWW.Tumblr.COM');` |
| `osint_normalize_profile_url` | `osint_normalize_profile_url(url) → STRING` | Canonicalize profile URL while dropping query and fragment state. | `SELECT osint_normalize_profile_url(profile_url);` |
| `osint_normalize_repository_url` | `osint_normalize_repository_url(url) → STRING` | Canonicalize HTTP(S) repository URL and remove trailing .git. | `SELECT osint_normalize_repository_url(repo_url);` |
| `osint_normalize_username` | `osint_normalize_username(value) → STRING` | Trim username, remove leading @ markers, NFC-normalize; preserve provider-specific case. | `SELECT osint_normalize_username(' @@User.Name ');` |
| `osint_normalize_verification_status` | `osint_normalize_verification_status(value) → STRING` | Map verification labels to controlled vocabulary such as unverified/machine_correlated/confirmed. | `SELECT osint_normalize_verification_status(status);` |
| `osint_redact_url_secrets` | `osint_redact_url_secrets(url) → STRING` | Remove/redact URL credentials and sensitive query parameters before storage/logging. | `SELECT osint_redact_url_secrets(request_url);` |
