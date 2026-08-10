# ETL Research — Domain Matrix

Research matrix này rộng hơn public scalar API. Cột **Repository status** phân biệt rõ: đã có UDF, dùng generic UDF, hay để ở parser/enrichment/reference-data layer.

| Domain | Representative data | ETL / normalization operations | Typical use | Open-source building blocks | Repository status |
| --- | --- | --- | --- | --- | --- |
| Security / SOC | IPv4, IPv6, CIDR, ASN, MAC | Canonical IP/CIDR/ASN, GeoIP/RDAP enrichment | SIEM correlation | MaxMind GeoIP2, ipwhois | `normalize_ip`, `normalize_cidr`, `net_normalize_asn`; GeoIP/RDAP external |
| Security / Logs | Syslog, firewall, WAF, IDS | Grok parsing, timestamp/protocol normalization | Structured SIEM events | Logstash Grok | Parser stage; `etl_normalize_iso_datetime` and text helpers available |
| Security / CTI | STIX, CVE, ATT&CK, IOC hashes | STIX/CVE/ATT&CK/digest canonicalization | CTI interchange | python-stix2, STIX Validator | `cti_*`, `security_*`; full STIX validation external |
| Security / Malware | Binary, MD5/SHA, YARA | Digest normalization/classification, MIME/magic-byte, YARA | Malware dedup / IOC | YARA, YARA-X | Hash UDFs available; binary/YARA parsing external |
| Banking / Privacy | PAN, PII, account data | Masking, fingerprinting, tokenization | Privacy-safe processing | Presidio | Mask/fingerprint UDFs available; token vault external |
| Banking / Money | Amount, currency, rate | Decimal normalization, currency shape, percentage | Reconciliation | Python `decimal`, Babel | `etl_normalize_decimal`, currency/percentage helpers |
| Banking / Payments | IBAN, BIC, ISO 20022 | IBAN checksum, BIC syntax, message identifier | Payment integration | schwifty, Moov ISO20022 | `finance_*`; XML/XSD parsing external |
| Legal entity / Compliance | LEI | ISO 17442 normalization/checksum | Registry linkage | OpenSanctions | `finance_normalize_lei`; watchlist/entity matching external |
| Citizen / Identity | CCCD, CMND, passport | Structural normalization/classification | Cross-system identity linking | python-stdnum | `vn_normalize_citizen_id`, `vn_classify_identity_id`; authoritative validation external |
| Citizen / Names | Vietnamese/multilingual names | Unicode NFC, whitespace, search key | Search / entity-resolution blocking | ICU | Generic `etl_normalize_person_name`, `etl_latin_name_search_key` |
| Citizen / Address | Free-text address, admin codes | Text cleanup, parse, geocode, admin-code mapping | Cross-source matching | libpostal, Nominatim | `etl_normalize_address_text`; parsing/geocoding/reference joins external |
| Tax / Enterprise | Vietnamese MST | Structural formatting/classification | Tax registry linkage | python-stdnum | `vn_normalize_tax_id`, `vn_classify_tax_id_structure`; registry validation external |
| eKYC | Images, Base64 payload | Decode limits, MIME, hashing, object-storage handoff | Secure document handling | Pillow/OpenCV, Presidio Image | File/image parser stage; mask/hash helpers available |
| eKYC / Scores | Liveness, face-match score | Probability/range validation | Fraud decision pipeline | Validation frameworks | `etl_normalize_probability`, `etl_quality_number_in_range`; thresholds external config |
| OCR / Documents | OCR JSON, bbox, confidence | JSON flatten/canonicalize, text cleanup | Relational/search mapping | Tesseract, Unstructured | JSON/text UDFs available; OCR external |
| Healthcare / FHIR | FHIR ID/reference | ID/reference syntax normalization | EHR interoperability | HAPI FHIR | `health_normalize_fhir_id`, `health_normalize_fhir_reference`; profile validation external |
| Healthcare / HL7 v2 | MSH message type, segments | Message type normalization, message parsing | HIS/LIS/RIS | HL7apy | `health_normalize_hl7_message_type`; full parser external |
| Healthcare / DICOM | Study/Series/SOP UID, files | UID validation, de-identification, metadata extraction | PACS analytics | pydicom | `health_normalize_dicom_uid`; modality terminology/file parsing external |
| Healthcare / Units | Lab values, unit codes | Unit conversion, terminology mapping | Cross-hospital comparison | Pint, UCUM tooling | Reference/terminology layer; no scalar UDF shipped |
| Telecom | MSISDN, IMSI, IMEI | E.164, identifier validation, masking | Subscriber analytics | libphonenumber, pycrate | Generic `etl_normalize_e164`; IMSI/IMEI not implemented |
| Telecom / CDR | ASN.1/BER CDR | ASN.1 decode, vendor schema, flatten | Billing/QoS | pycrate | Parser stage |
| Education | Student/teacher/school IDs | Generic code normalization, reference lookup | Multi-source education integration | Domain reference data | Use `etl_normalize_identifier_code`; no education-specific aliases |
| Learning analytics | xAPI | Statement schema validation / dedupe | LRS analytics | xapi-schema | Parser/validator candidate; no scalar UDF shipped |
| E-commerce | Product/SKU/attributes | JSON flatten, decimal/range validation | Catalog integration | JSON Schema | Generic JSON/decimal/quality UDFs; taxonomy external |
| Entity resolution | Person/company/product aliases | Search keys, blocking, probabilistic matching | Dedup/cross-source linkage | RapidFuzz, Splink, dedupe | Generic Latin search key only; probabilistic matching external |
| Supply chain | GTIN, SSCC, EPCIS | Check digit, event class normalization | Traceability | OpenEPCIS | `supply_normalize_gtin`, `supply_normalize_sscc`, `supply_normalize_epcis_event_type` |
| Public transport | GTFS feed | Feed-level validation, foreign keys, coordinates | Journey planning | MobilityData GTFS Validator | GTFS ID helper removed; feed validation external, coordinates use `geo_*` |
| GIS | CRS/EPSG, coordinates, geometry/raster | EPSG/coordinate validation, CRS transform, geometry repair | Spatial analytics | GDAL, PROJ, H3 | `geo_*` scalar helpers; geometry/raster external |
| Manufacturing | OPC UA NodeId | NodeId canonicalization, units/quality lookup | SCADA ingestion | open62541 | `iot_normalize_opcua_node_id`; protocol/quality semantics external |
| Energy / Metering | DLMS/COSEM, OBIS | OBIS syntax, interval/unit normalization | Smart-meter analytics | Gurux DLMS | `iot_normalize_obis_code`; protocol client external |
| IoT | MQTT topic/payload | Decode JSON/CBOR/Protobuf, event-time/unit normalization | Telemetry | Eclipse Paho, Telegraf | Decode/protocol external; generic JSON/time UDFs available |
| Climate / Ocean | NetCDF, GRIB, CF metadata | File decode, CF/GRIB table validation | Climate analytics | xarray, cfgrib, ecCodes | Scalar climate helpers removed; parser/reference-data layer |
| Documents | PDF, Office, HTML, WARC | Text/MIME extraction, OCR, hashing | Search/RAG | Apache Tika, Unstructured, warcio | MIME/JSON/text/hash helpers; document parser external |
| Legal | Contracts, regulations | Structure/entity/date/amount extraction | Legal search | LexNLP | Parser/enrichment layer |
| Media | Audio/video/subtitles | Codec/container parse, transcoding | Media lake | FFmpeg | Parser/transcode stage |
| Genomics | SAM/BAM/CRAM/VCF/BCF | File parsing, variant normalization, reference validation | Genomic analytics | HTSlib, BCFtools | Scalar genomics helpers removed; specialized parser layer |
| Astronomy | FITS/WCS | FITS/WCS parse, coordinate frames | Astronomy integration | Astropy | Scalar astronomy helpers removed; specialized parser layer |
| Insurance | ACORD XML, policy, coverage | XML/XSD validation, domain mapping | Insurance integration | ACORD implementations | Scalar insurance helpers removed; schema-aware parser/reference layer |

## Ghi chú

Việc một loại dữ liệu xuất hiện trong research **không đồng nghĩa** phải có UDF riêng. Nếu logic chỉ là trim/uppercase/rename hoặc cần danh mục versioned, parser hay network lookup thì không đưa vào public scalar API.
