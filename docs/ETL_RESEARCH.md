# ETL Library Research — Domain Data Normalization Roadmap

This document preserves the research used to design `flink-etl-udfs`. The repository focuses on deterministic, reusable transforms that are safe to execute as PyFlink scalar UDFs. Parsers that require file access, network I/O, large reference datasets, model inference, or stateful matching are intentionally treated as upstream parser/enrichment stages.

## Design principles derived from the research

1. **Atomic transforms first.** Build small reusable normalizers such as text, time, identifiers, money, URLs, hashes, and quality checks.
2. **Domain profiles second.** Country-, industry-, or standard-specific rules live in separate modules and registries.
3. **Do not hide I/O in scalar UDFs.** DNS/RDAP, geocoding, crawler calls, terminology lookup, model inference, file parsing, and registry validation belong in enrichment/parser operators.
4. **Preserve raw + canonical values.** Normalization can be lossy; retain source values and provenance.
5. **Return `NULL` for invalid scalar inputs.** Pipelines can route invalid rows to quarantine/data-quality handling instead of throwing per-record exceptions.
6. **Keep evidence and confidence explicit.** Especially for OSINT/entity-resolution data, normalized equality does not prove identity.

## Detailed research files

- [Domain research matrix](research/domain-matrix.md)
- [OSINT research](research/osint.md)

## Repository implementation tiers

### P0 — common transforms

- null-token normalization
- ISO date/time normalization
- decimal/percentage/probability normalization
- currency code shape
- E.164 shape normalization
- JSON canonicalization/flattening/validation
- generic data-quality checks
- deterministic record IDs
- masking/fingerprinting/text/IP helpers

### P1 — Vietnam / citizen / education / banking

- CMND/CCCD structural normalization/classification
- Vietnamese tax ID normalization/classification
- Vietnamese phone/name/address normalization
- accent-insensitive name search key
- school/teacher/student codes
- academic year
- SMS brand name
- bank account identifier
- entity blocking key

### P2 — standards and operational domains

- OSINT observation/entity/evidence helpers
- STIX/MITRE CTI identifiers
- FHIR/HL7/DICOM identifiers
- IBAN/BIC/ISO 20022 message type
- GTIN/SSCC/EPCIS event type
- OPC UA/OBIS/telemetry quality
- GTFS ID / latitude / longitude / EPSG

### P3 — scientific and specialized domains

- chromosome / DNA / VCF genotype
- CF standard name / GRIB short name
- FITS keyword / celestial frame
- ACORD version / policy / coverage code

## Parser vs UDF boundary

The following integrations should not be implemented as normal scalar UDFs because they require file parsing, network access, schemas, reference datasets, or stateful processing:

- GeoIP, RDAP, DNS, geocoding
- STIX bundle/profile validation
- FHIR profile/terminology validation
- full HL7 v2 segment parsing
- DICOM file parsing/de-identification
- ISO 20022 and ACORD XML/XSD validation
- EPCIS XML/JSON-LD parsing
- OPC UA / DLMS protocol clients
- GTFS ZIP/feed validation
- raster/vector geometry processing with GDAL/PROJ/H3
- NetCDF/GRIB/FITS/SAM/BAM/CRAM/VCF file parsing
- OCR, media transcoding, EXIF extraction
- probabilistic entity resolution, sanctions matching, identity attribution

Those components should output canonical records into Kafka/files/tables, after which this repository's deterministic UDFs can normalize fields inside Flink SQL.

## License and reference-data note

Before production use, separately review the license of **code**, **models/reference datasets**, and **standards/specifications**. Some libraries are permissive while associated datasets, schemas, terminology systems, or country-specific reference data may have independent usage restrictions.
