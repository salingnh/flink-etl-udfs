# ETL Research — OSINT

## OSINT-specific research

OSINT data needs an explicit separation between **observation**, **entity**, and **evidence**. A normalized username, email, phone, profile URL, or name-search key is only a candidate correlation signal; it must not be treated as proof that two records represent the same person.

| OSINT category | Representative data | ETL / normalization | Open-source building blocks | Repository status |
| --- | --- | --- | --- | --- |
| Username / account discovery | username, handle, platform, profile URL | handle/platform normalization, profile URL canonicalization, found-status normalization | [Sherlock](https://github.com/sherlock-project/sherlock), [Maigret](https://github.com/soxoj/maigret) | Implemented scalar normalizers; collectors external |
| Social profile snapshot | UID, display name, bio, avatar, observation time | stable profile URL, observed-at UTC, content hash, observation ID | Platform-specific collectors | Evidence/provenance helpers implemented |
| Email / organization footprint | email, domain, MX/SPF/DKIM/DMARC | email/domain normalization and DNS enrichment | [theHarvester](https://github.com/laramies/theHarvester) | Email/domain scalar normalization implemented; DNS enrichment external |
| Domain / subdomain | FQDN, DNS record types | IDNA/domain normalization, DNS type normalization | [OWASP Amass](https://github.com/owasp-amass/amass), [Subfinder](https://github.com/projectdiscovery/subfinder) | Implemented scalar normalizers; enumeration external |
| IP / ASN | IP, ASN, netblock | canonical IP/ASN, RDAP enrichment | [ipwhois](https://github.com/secynic/ipwhois) | IP/ASN scalar helpers implemented; RDAP external |
| Website content | URL, title, article body, links | URL canonicalization, tracking/secret removal, content hashing | [Trafilatura](https://github.com/adbar/trafilatura) | URL/evidence helpers implemented; crawler/parser external |
| Web archive | WARC, archived URL, crawl time | payload hash, URL/time normalization | [warcio](https://github.com/webrecorder/warcio) | Evidence helpers implemented; WARC parser external |
| Image metadata | EXIF/XMP/IPTC, GPS, file hash | hash and metadata normalization | [ExifTool](https://exiftool.org/) | File hash available; EXIF extraction external |
| Video/audio metadata | title, duration, subtitles, uploader | media metadata normalization | [yt-dlp](https://github.com/yt-dlp/yt-dlp), FFmpeg | Collector/parser stage |
| Geolocation | address, place, coordinates | address text, coordinate/CRS validation, geocoding | [geopy](https://github.com/geopy/geopy), PROJ/GDAL | Coordinate/CRS scalar helpers implemented; geocoding external |
| Company / watchlist | entity, alias, LEI, ownership, sanctions | LEI/ownership/entity type, entity matching | [OpenSanctions](https://github.com/opensanctions/opensanctions), [Aleph](https://github.com/alephdata/aleph) | LEI/ownership/entity-type scalar helpers implemented; matching external |
| Source-code OSINT | repository URL, git object ID | repo URL canonicalization and full hash normalization | Git platform APIs | Implemented |
| Credential exposure | account identifier, URL, incident/IOC, remediation state | identifier/URL/IOC/exposure-status normalization, strict access policy | No single generally safe public source | Scalar normalization implemented; acquisition intentionally outside repo |
| Graph / link analysis | person-account, domain-IP, company-person edges | stable entity/observation IDs, confidence, verification status | [SpiderFoot](https://github.com/smicallef/spiderfoot), Aleph | IDs/confidence/status helpers implemented; graph inference external |
