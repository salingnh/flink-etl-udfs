# ETL Library Research — Domain Data Normalization Roadmap

Tài liệu này giữ lại research dùng để thiết kế `flink-etl-udfs`. Research matrix rộng hơn public API: không phải mọi data type được nghiên cứu đều phù hợp trở thành scalar UDF.

## Nguyên tắc sau cleanup 0.5.0

1. **Atomic/generic transforms trước.** Text, time, decimal, identifiers, JSON, URL, hash và quality checks phải tái sử dụng được giữa nhiều nguồn.
2. **Domain function chỉ khi thật sự có semantics riêng.** Ví dụ CMND/CCCD, MST Việt Nam, IBAN, BIC, LEI, GTIN/SSCC, STIX/FHIR/DICOM UID.
3. **Không giữ compatibility alias.** Dataset-specific wrapper bị xóa thay vì duy trì song song generic function.
4. **Không giấu I/O trong scalar UDF.** DNS/RDAP, geocoding, crawler, terminology lookup, file parsing và registry validation nằm ở parser/enrichment layer.
5. **Không hard-code reference list thay đổi theo thời gian.** ISO currency list, BIC directory, EPSG registry, FHIR ValueSet, CVE/ATT&CK metadata... phải là versioned reference data.
6. **Preserve raw + canonical values** khi normalization có thể lossy.

## Detailed research files

- [Domain research matrix](research/domain-matrix.md)
- [OSINT research](research/osint.md)

## Public scalar tiers hiện tại

### P0 — common/generic

- null token, Unicode, whitespace, person name, address-text preprocessing
- ISO 8601 date/time, Decimal, percentage, probability
- ISO 4217-shaped currency code, E.164-shaped phone number
- JSON canonicalization/flattening/validation
- data-quality checks, deterministic record ID, masking/fingerprinting
- IP/CIDR, email và generic business identifier code

### Internet / security / code

- IDNA domain, HTTP(S) canonical URL, secret redaction, ASN, DNS RR type, MIME type
- MD5/SHA digest shape, CVE, STIX ID/type, MITRE ATT&CK technique ID
- Git repository URL và full Git SHA-1/SHA-256 object ID

### Vietnam-specific

- CMND/CCCD structural normalization/classification
- MST structural normalization và `base_10` / `extended_13` classification

### Specialized standards

- FHIR resource/reference, HL7 v2 message type, DICOM UID
- IBAN, BIC, ISO 20022 message type, LEI
- GS1 GTIN/SSCC/EPCIS event type
- OPC UA NodeId, DLMS/COSEM OBIS
- latitude, longitude, EPSG code shape

## Research candidates không còn là scalar UDF

Các nhóm sau vẫn nằm trong research nhưng đã bị xóa khỏi public/core UDF surface vì semantics quá mỏng, dễ gây hiểu nhầm hoặc cần parser/reference data chuyên dụng:

- education-specific code aliases, academic-year helper, SMS brand vocabulary, entity blocking composite key;
- OSINT custom entity/status/platform vocabularies và duplicate confidence/time/percentage helpers;
- GTFS ID whitespace cleanup và telemetry-quality custom mapping;
- DICOM modality uppercase helper;
- scientific helpers cho chromosome/DNA/VCF, CF/GRIB, FITS/celestial frame;
- insurance/ACORD policy/coverage/version cleanup.

## Parser vs UDF boundary

Các integration sau nên chạy trước hoặc song song Flink SQL:

- GeoIP, RDAP, DNS query, geocoding
- STIX bundle/pattern/profile validation
- FHIR profile/terminology validation
- full HL7 v2 segment parsing
- DICOM file parsing/de-identification
- ISO 20022 và ACORD XML/XSD validation
- EPCIS XML/JSON-LD parsing
- OPC UA / DLMS protocol clients
- GTFS ZIP/feed validation
- GDAL/PROJ/H3 raster/vector processing
- NetCDF/GRIB/FITS/SAM/BAM/CRAM/VCF file parsing
- OCR, media transcoding, EXIF extraction
- probabilistic entity resolution, sanctions matching, identity attribution

Các stage này nên phát canonical records vào Kafka/Avro/Parquet/table; thư viện này xử lý row-level deterministic normalization sau đó.
