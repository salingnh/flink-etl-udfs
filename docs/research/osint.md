# ETL Research — OSINT

OSINT cần tách **observation**, **entity** và **evidence**. Normalized equality không phải bằng chứng hai record là cùng một người/tổ chức.

Sau cleanup `0.5.0`, `osint_*` chỉ còn semantics deterministic thật sự riêng cho observation/account handle. Các transform internet/security/code/finance dùng chung được chuyển sang pack generic tương ứng. External REST lookup dùng namespace `enrich_*` để phân biệt rõ với transform thuần.

| OSINT category | Representative data | ETL / normalization | Open-source building blocks | Cách triển khai trong repo |
| --- | --- | --- | --- | --- |
| Username / account discovery | username, handle, platform, profile URL | normalize handle; profile URL enrichment qua collector/service | Sherlock, Maigret, internal collectors | `osint_normalize_username`; `enrich_extract_profile_url` cho async REST extraction; `net_*` cho URL/domain canonicalization |
| Social profile snapshot | UID, bio, avatar, observation time | observation ID, ISO time, evidence hash | Platform-specific collectors | `osint_build_observation_id`, `etl_normalize_iso_datetime`, `sha256_fingerprint`; source metadata có thể lấy qua `enrich_extract_profile_url` |
| Email / organization footprint | email, domain, DNS metadata | email/domain normalization, DNS enrichment | theHarvester | `normalize_email`, `net_normalize_domain`; DNS lookup external |
| Domain / subdomain | FQDN, DNS record type | IDNA/domain normalization | Amass, Subfinder | `net_normalize_domain`, `net_normalize_dns_record_type`; enumeration external |
| IP / ASN | IP, ASN, netblock | canonical IP/ASN, RDAP enrichment | ipwhois | `normalize_ip`, `normalize_cidr`, `net_normalize_asn`; RDAP external |
| Website / archive | URL, HTML, WARC | canonical URL, secret redaction, content hash | Trafilatura, warcio | `net_canonicalize_url`, `net_redact_url_secrets`, `sha256_fingerprint`; crawling/WARC parsing external |
| Image/media metadata | EXIF/XMP/IPTC, file hash, codec | hash + metadata extraction | ExifTool, FFmpeg, yt-dlp | Hash UDF available; metadata parser external |
| Geolocation | address, coordinates, CRS | address text, coordinate range, CRS code | geopy, PROJ/GDAL | `etl_normalize_address_text`, `geo_*`; geocoding external |
| Company / watchlist | LEI, ownership, sanctions | LEI validation, ownership/reference matching | OpenSanctions, Aleph | `finance_normalize_lei`; ownership/status/entity vocabulary không hard-code vào UDF |
| Source-code OSINT | repository URL, Git object ID | repository canonicalization, full object ID normalization | Git platform APIs | `code_*` pack |
| Security / IOC | CVE, file hash, STIX/ATT&CK | identifier canonicalization | STIX/OASIS, MITRE | `security_*` và `cti_*` packs |
| Credential exposure | account, URL, incident, remediation state | strict access policy + generic identifier/URL/IOC transforms | Authorized/internal sources only | Không có custom exposure-status vocabulary; dùng source schema/reference data |
| Graph / link analysis | person-account, domain-IP, company-person | observation IDs, score, verification workflow | SpiderFoot, Aleph | `osint_build_observation_id`, `etl_normalize_probability`; graph inference/status external |

Collector, sanctions matching, entity attribution, RDAP/DNS query, geocoding, crawler và credential acquisition không thuộc **synchronous scalar UDF** layer. Khi một lookup nhỏ cần xuất hiện trực tiếp trong Flink SQL, dùng async enrichment với timeout/retry/concurrency rõ ràng; `enrich_extract_profile_url` là implementation đầu tiên theo pattern này.
