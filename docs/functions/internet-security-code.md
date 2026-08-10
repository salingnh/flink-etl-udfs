# Internet, Security / CTI và Source Code

## Internet / DNS / URL

Đăng ký bằng `register_internet_udfs(t_env)`.

| Tên hiển thị | SQL function | Chuẩn / phạm vi | Mô tả | Giá trị trước → sau | Ví dụ SQL |
| --- | --- | --- | --- | --- | --- |
| Canonical URL | `net_canonicalize_url` | HTTP(S) | Lowercase scheme/host, bỏ credentials, fragment, tracking params và sort query. | `HTTPS://user:pass@Example.COM:443/a?utm_source=x&id=12#top` → `https://example.com/a?id=12` | `SELECT net_canonicalize_url(source_url);` |
| Lấy hostname từ URL | `net_extract_url_host` | HTTP(S) | Canonicalize URL rồi lấy hostname. | `https://Portal.EXAMPLE.GOV.VN/a?id=1` → `portal.example.gov.vn` | `SELECT net_extract_url_host(source_url);` |
| Chuẩn hóa ASN | `net_normalize_asn` | 32-bit ASN | Chuẩn hóa Autonomous System Number về `AS<number>`. | `as13335` → `AS13335` | `SELECT net_normalize_asn(asn);` |
| Chuẩn hóa DNS RR type | `net_normalize_dns_record_type` | DNS | Uppercase và chỉ nhận record type phổ biến được hỗ trợ. | `aaaa` → `AAAA` | `SELECT net_normalize_dns_record_type(record_type);` |
| Chuẩn hóa domain | `net_normalize_domain` | DNS / IDNA | Bỏ trailing dot, chuyển Unicode domain sang IDNA ASCII và lowercase. | `BÜCHER.DE.` → `xn--bcher-kva.de` | `SELECT net_normalize_domain(domain);` |
| Chuẩn hóa MIME type | `net_normalize_mime_type` | MIME | Lowercase media type và bỏ parameter như charset. | `Text/HTML; charset=UTF-8` → `text/html` | `SELECT net_normalize_mime_type(content_type);` |
| Che secret trong URL | `net_redact_url_secrets` | Logging safety | Bỏ URL userinfo và redact token/password/api-key trong query. | `https://api.example.vn/a?token=abc&id=12` → `https://api.example.vn/a?token=%5BREDACTED%5D&id=12` | `SELECT net_redact_url_secrets(request_url);` |

## Security / CTI

Đăng ký bằng `register_security_udfs(t_env)`.

| Tên hiển thị | SQL function | Chuẩn / phạm vi | Mô tả | Giá trị trước → sau | Ví dụ SQL |
| --- | --- | --- | --- | --- | --- |
| Chuẩn hóa MITRE ATT&CK ID | `cti_normalize_attack_technique_id` | MITRE ATT&CK | Chuẩn hóa technique/sub-technique ID. | `t1059.001` → `T1059.001` | `SELECT cti_normalize_attack_technique_id(technique_id);` |
| Chuẩn hóa STIX ID | `cti_normalize_stix_id` | STIX 2.x identifier | Validate `type--uuid` và canonicalize UUID. | `indicator--550e8400-e29b-41d4-a716-446655440000` → cùng canonical STIX ID | `SELECT cti_normalize_stix_id(stix_id);` |
| Chuẩn hóa STIX type | `cti_normalize_stix_type` | STIX type token | Lowercase và chuyển `_` sang `-`; full object validation nằm ở STIX validator. | `MALWARE_ANALYSIS` → `malware-analysis` | `SELECT cti_normalize_stix_type(stix_type);` |
| Phân loại digest | `security_classify_hash_type` | MD5/SHA family | Xác định loại hash theo độ dài digest hex hợp lệ. | `64 ký tự hex` → `sha256` | `SELECT security_classify_hash_type(file_hash);` |
| Chuẩn hóa CVE | `security_normalize_cve` | CVE identifier | Chuẩn hóa về `CVE-YYYY-NNNN...`; không lookup CVE record. | `cve 2024 12345` → `CVE-2024-12345` | `SELECT security_normalize_cve(cve_id);` |
| Chuẩn hóa digest hex | `security_normalize_hex_hash` | MD5/SHA family | Lowercase digest và chỉ nhận độ dài phổ biến 32/40/64/128. | `AAAAAAAA...` 64 ký tự → `aaaaaaaa...` 64 ký tự | `SELECT security_normalize_hex_hash(file_hash);` |

## Source code / Git

Đăng ký bằng `register_code_udfs(t_env)`.

| Tên hiển thị | SQL function | Chuẩn / phạm vi | Mô tả | Giá trị trước → sau | Ví dụ SQL |
| --- | --- | --- | --- | --- | --- |
| Phân loại Git object hash | `code_classify_git_object_hash` | Git object ID | Full 40 hex → `sha1`, full 64 hex → `sha256`. | `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa` → `sha1` | `SELECT code_classify_git_object_hash(commit_hash);` |
| Chuẩn hóa Git object ID | `code_normalize_git_object_id` | Git full SHA-1/SHA-256 | Lowercase full object ID và reject abbreviated hash. | `AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA` → `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa` | `SELECT code_normalize_git_object_id(commit_hash);` |
| Chuẩn hóa repository URL | `code_normalize_repository_url` | HTTP(S) Git repository | Canonicalize URL và bỏ suffix `.git`, query/fragment. | `https://github.com/org/repo.git?utm_source=x` → `https://github.com/org/repo` | `SELECT code_normalize_repository_url(repo_url);` |
