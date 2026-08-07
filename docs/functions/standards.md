# Standards and Specialized Domain Functions

## CTI / STIX / MITRE ATT&CK

Register with `register_security_standard_udfs(t_env)`.

| SQL function | Signature | Description | Example |
| --- | --- | --- | --- |
| `cti_normalize_attack_technique_id` | `cti_normalize_attack_technique_id(value) → STRING` | Normalize ATT&CK technique/sub-technique ID such as T1059 or T1059.001. | `SELECT cti_normalize_attack_technique_id(technique_id);` |
| `cti_normalize_stix_id` | `cti_normalize_stix_id(value) → STRING` | Normalize/validate STIX ID of form type--uuid. | `SELECT cti_normalize_stix_id(stix_id);` |
| `cti_normalize_stix_type` | `cti_normalize_stix_type(value) → STRING` | Normalize STIX object type token to lowercase hyphenated form. | `SELECT cti_normalize_stix_type(stix_type);` |

## Healthcare

Register with `register_healthcare_udfs(t_env)`.

| SQL function | Signature | Description | Example |
| --- | --- | --- | --- |
| `health_normalize_dicom_modality` | `health_normalize_dicom_modality(value) → STRING` | Normalize DICOM Modality code to uppercase syntax. | `SELECT health_normalize_dicom_modality(modality);` |
| `health_normalize_dicom_uid` | `health_normalize_dicom_uid(value) → STRING` | Validate DICOM UID/OID syntax and 64-character length limit. | `SELECT health_normalize_dicom_uid(study_uid);` |
| `health_normalize_fhir_id` | `health_normalize_fhir_id(value) → STRING` | Validate FHIR resource id character/length constraints. | `SELECT health_normalize_fhir_id(resource_id);` |
| `health_normalize_fhir_reference` | `health_normalize_fhir_reference(value) → STRING` | Normalize relative/local FHIR reference such as Patient/123 or #contained. | `SELECT health_normalize_fhir_reference(subject_ref);` |
| `health_normalize_hl7_message_type` | `health_normalize_hl7_message_type(value) → STRING` | Normalize HL7 v2 message type such as ADT^A01. | `SELECT health_normalize_hl7_message_type(message_type);` |

## Finance / payment standards

Register with `register_finance_udfs(t_env)`.

| SQL function | Signature | Description | Example |
| --- | --- | --- | --- |
| `finance_normalize_bic` | `finance_normalize_bic(value) → STRING` | Normalize 8/11-character BIC/SWIFT code to uppercase; validate syntax. | `SELECT finance_normalize_bic(bic);` |
| `finance_normalize_iban` | `finance_normalize_iban(value) → STRING` | Remove spaces, uppercase and validate IBAN using mod-97. | `SELECT finance_normalize_iban(iban);` |
| `finance_normalize_iso20022_message_type` | `finance_normalize_iso20022_message_type(value) → STRING` | Normalize ISO 20022 message identifier such as pacs.008.001.08. | `SELECT finance_normalize_iso20022_message_type(message_type);` |

## Supply chain / GS1 / EPCIS

Register with `register_supply_chain_udfs(t_env)`.

| SQL function | Signature | Description | Example |
| --- | --- | --- | --- |
| `supply_normalize_epcis_event_type` | `supply_normalize_epcis_event_type(value) → STRING` | Map EPCIS event aliases to canonical class name. | `SELECT supply_normalize_epcis_event_type(event_type);` |
| `supply_normalize_gtin` | `supply_normalize_gtin(value) → STRING` | Normalize GTIN-8/12/13/14 and validate GS1 check digit. | `SELECT supply_normalize_gtin(gtin);` |
| `supply_normalize_sscc` | `supply_normalize_sscc(value) → STRING` | Normalize 18-digit SSCC and validate GS1 check digit. | `SELECT supply_normalize_sscc(sscc);` |

## Industrial / IoT / metering

Register with `register_industrial_udfs(t_env)`.

| SQL function | Signature | Description | Example |
| --- | --- | --- | --- |
| `iot_normalize_obis_code` | `iot_normalize_obis_code(value) → STRING` | Normalize common textual DLMS/COSEM OBIS form A-B:C.D.E*F; syntax validation only. | `SELECT iot_normalize_obis_code(obis);` |
| `iot_normalize_opcua_node_id` | `iot_normalize_opcua_node_id(value) → STRING` | Normalize OPC UA NodeId namespace and identifier-type prefix. | `SELECT iot_normalize_opcua_node_id(node_id);` |
| `iot_normalize_telemetry_quality` | `iot_normalize_telemetry_quality(value) → STRING` | Map common quality labels to good/uncertain/bad/offline. | `SELECT iot_normalize_telemetry_quality(quality);` |

## Transport / geospatial

Register with `register_transport_geo_udfs(t_env)`.

| SQL function | Signature | Description | Example |
| --- | --- | --- | --- |
| `geo_normalize_epsg_code` | `geo_normalize_epsg_code(value) → STRING` | Normalize numeric CRS identifier to EPSG:<code>. | `SELECT geo_normalize_epsg_code('4326');` |
| `geo_normalize_latitude` | `geo_normalize_latitude(value) → DOUBLE` | Parse latitude in inclusive -90..90 range. | `SELECT geo_normalize_latitude(latitude);` |
| `geo_normalize_longitude` | `geo_normalize_longitude(value) → DOUBLE` | Parse longitude in inclusive -180..180 range. | `SELECT geo_normalize_longitude(longitude);` |
| `gtfs_normalize_id` | `gtfs_normalize_id(value) → STRING` | Trim/collapse whitespace in GTFS identifier while rejecting line breaks. | `SELECT gtfs_normalize_id(stop_id);` |

## Scientific data

Register with `register_scientific_udfs(t_env)`.

| SQL function | Signature | Description | Example |
| --- | --- | --- | --- |
| `astro_normalize_celestial_frame` | `astro_normalize_celestial_frame(value) → STRING` | Normalize common celestial coordinate-frame aliases to a controlled frame name. | `SELECT astro_normalize_celestial_frame(frame);` |
| `astro_normalize_fits_keyword` | `astro_normalize_fits_keyword(value) → STRING` | Normalize FITS header keyword to uppercase syntax. | `SELECT astro_normalize_fits_keyword('date-obs');` |
| `climate_normalize_cf_standard_name` | `climate_normalize_cf_standard_name(value) → STRING` | Normalize CF-style variable name to lowercase underscore form. | `SELECT climate_normalize_cf_standard_name('Air Temperature');` |
| `climate_normalize_grib_short_name` | `climate_normalize_grib_short_name(value) → STRING` | Normalize GRIB short-name token to lowercase syntax; no parameter-table lookup. | `SELECT climate_normalize_grib_short_name(short_name);` |
| `genomics_normalize_chromosome` | `genomics_normalize_chromosome(value) → STRING` | Remove chr prefix, uppercase, map mitochondrial M to MT. | `SELECT genomics_normalize_chromosome('chrM');` |
| `genomics_normalize_dna_sequence` | `genomics_normalize_dna_sequence(value) → STRING` | Uppercase and validate IUPAC DNA symbols. | `SELECT genomics_normalize_dna_sequence(sequence);` |
| `genomics_normalize_vcf_genotype` | `genomics_normalize_vcf_genotype(value) → STRING` | Validate VCF genotype token while preserving phased/unphased separator. | `SELECT genomics_normalize_vcf_genotype('0/1');` |

## Insurance / ACORD

Register with `register_insurance_udfs(t_env)`.

| SQL function | Signature | Description | Example |
| --- | --- | --- | --- |
| `insurance_normalize_acord_version` | `insurance_normalize_acord_version(value) → STRING` | Normalize ACORD version label to compact numeric form. | `SELECT insurance_normalize_acord_version('ACORD v2.0');` |
| `insurance_normalize_coverage_code` | `insurance_normalize_coverage_code(value) → STRING` | Normalize coverage code to uppercase underscore-separated text. | `SELECT insurance_normalize_coverage_code(coverage_code);` |
| `insurance_normalize_policy_number` | `insurance_normalize_policy_number(value) → STRING` | Normalize policy identifier to uppercase compact conservative syntax. | `SELECT insurance_normalize_policy_number(policy_no);` |
