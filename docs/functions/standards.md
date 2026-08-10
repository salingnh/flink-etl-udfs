# Chuẩn quốc tế và domain chuyên ngành

Các function trong file này ưu tiên chuẩn trao đổi dữ liệu phổ biến. Mô tả ghi rõ function đang làm **canonicalization**, **syntax validation**, **checksum**, hay cần thêm **reference-data lookup**.

## CTI / STIX / MITRE ATT&CK

Đăng ký bằng `register_security_standard_udfs(t_env)`.

| Tên hiển thị | SQL function | Chuẩn / mức validation | Mô tả | Giá trị trước → sau | Ví dụ SQL |
| --- | --- | --- | --- | --- | --- |
| Chuẩn hóa ATT&CK Technique ID | `cti_normalize_attack_technique_id` | MITRE ATT&CK syntax | Uppercase và canonicalize technique/sub-technique ID. Không lookup metadata technique. | `t1059_001` → `T1059.001` | `SELECT cti_normalize_attack_technique_id(technique_id);` |
| Chuẩn hóa STIX ID | `cti_normalize_stix_id` | STIX identifier syntax + UUID parse | Validate dạng `type--uuid`, canonicalize UUID. | `indicator--550e8400-e29b-41d4-a716-446655440000` → cùng giá trị canonical | `SELECT cti_normalize_stix_id(stix_id);` |
| Chuẩn hóa STIX object type | `cti_normalize_stix_type` | STIX token syntax | Lowercase và đổi underscore thành hyphen cho object type token. | `malware_analysis` → `malware-analysis` | `SELECT cti_normalize_stix_type(stix_type);` |

## Y tế: FHIR / HL7 v2 / DICOM

Đăng ký bằng `register_healthcare_udfs(t_env)`.

| Tên hiển thị | SQL function | Chuẩn / mức validation | Mô tả | Giá trị trước → sau | Ví dụ SQL |
| --- | --- | --- | --- | --- | --- |
| Chuẩn hóa DICOM Modality | `health_normalize_dicom_modality` | DICOM syntax-only | Uppercase modality code và kiểm tra syntax bảo thủ. Không kiểm tra code có thuộc DICOM controlled terms hiện hành. | `ct` → `CT` | `SELECT health_normalize_dicom_modality(modality);` |
| Chuẩn hóa DICOM UID | `health_normalize_dicom_uid` | DICOM UID/OID syntax | Validate numeric-dot UID và giới hạn 64 ký tự. | `1.2.840.10008.1.2.1` → `1.2.840.10008.1.2.1` | `SELECT health_normalize_dicom_uid(study_uid);` |
| Kiểm tra FHIR Resource ID | `health_normalize_fhir_id` | FHIR id syntax | Validate charset/length của FHIR resource id, giữ nguyên giá trị canonical. | `patient-001` → `patient-001` | `SELECT health_normalize_fhir_id(resource_id);` |
| Chuẩn hóa FHIR Reference | `health_normalize_fhir_reference` | FHIR relative/local reference syntax | Validate `ResourceType/id` hoặc `#contained-id`. Không resolve reference qua server. | `Patient/patient-001` → `Patient/patient-001` | `SELECT health_normalize_fhir_reference(subject_ref);` |
| Chuẩn hóa HL7 v2 Message Type | `health_normalize_hl7_message_type` | HL7 v2 message-type syntax | Uppercase, normalize separator về `^` và kiểm tra dạng như `ADT^A01`. | `adt~a01` → `ADT^A01` | `SELECT health_normalize_hl7_message_type(message_type);` |

## Tài chính / thanh toán quốc tế

Đăng ký bằng `register_finance_udfs(t_env)`.

| Tên hiển thị | SQL function | Chuẩn / mức validation | Mô tả | Giá trị trước → sau | Ví dụ SQL |
| --- | --- | --- | --- | --- | --- |
| Chuẩn hóa BIC | `finance_normalize_bic` | ISO 9362 syntax | Remove whitespace, uppercase và validate cấu trúc BIC 8/11 ký tự. Không xác minh tổ chức/BIC còn active. | `deut de ff` → `DEUTDEFF` | `SELECT finance_normalize_bic(bic);` |
| Chuẩn hóa IBAN | `finance_normalize_iban` | ISO 13616 generic structure + mod-97 | Remove whitespace, uppercase, validate generic IBAN shape và mod-97. Không thay thế country-specific IBAN registry length/rule lookup. | `GB82 WEST 1234 5698 7654 32` → `GB82WEST12345698765432` | `SELECT finance_normalize_iban(iban);` |
| Chuẩn hóa ISO 20022 message type | `finance_normalize_iso20022_message_type` | ISO 20022 message identifier syntax | Lowercase và normalize `_` thành `.` cho identifier dạng `pacs.008.001.08`. | `PACS_008_001_08` → `pacs.008.001.08` | `SELECT finance_normalize_iso20022_message_type(message_type);` |

## Supply chain / GS1 / EPCIS

Đăng ký bằng `register_supply_chain_udfs(t_env)`.

| Tên hiển thị | SQL function | Chuẩn / mức validation | Mô tả | Giá trị trước → sau | Ví dụ SQL |
| --- | --- | --- | --- | --- | --- |
| Chuẩn hóa EPCIS event type | `supply_normalize_epcis_event_type` | GS1 EPCIS controlled event classes | Map alias về canonical class name như `ObjectEvent`, `AggregationEvent`. | `object_event` → `ObjectEvent` | `SELECT supply_normalize_epcis_event_type(event_type);` |
| Chuẩn hóa GTIN | `supply_normalize_gtin` | GS1 GTIN + check digit | Bỏ space/hyphen, nhận GTIN-8/12/13/14 và kiểm tra GS1 check digit. | `4006 3813 3393 1` → `4006381333931` | `SELECT supply_normalize_gtin(gtin);` |
| Chuẩn hóa SSCC | `supply_normalize_sscc` | GS1 SSCC + check digit | Bỏ separator, yêu cầu 18 chữ số và kiểm tra GS1 check digit. | `123456789012345675` → `123456789012345675` | `SELECT supply_normalize_sscc(sscc);` |

## Industrial / IoT / metering

Đăng ký bằng `register_industrial_udfs(t_env)`.

| Tên hiển thị | SQL function | Chuẩn / mức validation | Mô tả | Giá trị trước → sau | Ví dụ SQL |
| --- | --- | --- | --- | --- | --- |
| Chuẩn hóa OBIS code | `iot_normalize_obis_code` | DLMS/COSEM OBIS syntax-only | Normalize dạng text `A-B:C.D.E*F`, validate mỗi group 0..255. Không lookup semantic profile của meter/vendor. | `1-0:1.8.0*255` → `1-0:1.8.0*255` | `SELECT iot_normalize_obis_code(obis_code);` |
| Chuẩn hóa OPC UA NodeId | `iot_normalize_opcua_node_id` | OPC UA NodeId syntax | Canonicalize namespace và identifier-type prefix. | `NS=2;S=Temperature` → `ns=2;s=Temperature` | `SELECT iot_normalize_opcua_node_id(node_id);` |
| Chuẩn hóa quality telemetry | `iot_normalize_telemetry_quality` | Controlled ingestion vocabulary | Map label phổ biến về `good`, `uncertain`, `bad`, `offline`. | `OK` → `good` | `SELECT iot_normalize_telemetry_quality(quality);` |

## Transport / geospatial

Đăng ký bằng `register_transport_geo_udfs(t_env)`.

| Tên hiển thị | SQL function | Chuẩn / mức validation | Mô tả | Giá trị trước → sau | Ví dụ SQL |
| --- | --- | --- | --- | --- | --- |
| Chuẩn hóa EPSG CRS code | `geo_normalize_epsg_code` | EPSG identifier syntax | Chuẩn hóa numeric CRS identifier về `EPSG:<code>`. Không kiểm tra code có tồn tại trong EPSG registry. | `epsg:4326` → `EPSG:4326` | `SELECT geo_normalize_epsg_code(crs);` |
| Chuẩn hóa latitude | `geo_normalize_latitude` | WGS84-style numeric range | Parse float và chấp nhận miền `-90..90`. Không geocode hoặc validate location semantics. | `21.0278` → `21.0278` | `SELECT geo_normalize_latitude(latitude);` |
| Chuẩn hóa longitude | `geo_normalize_longitude` | WGS84-style numeric range | Parse float và chấp nhận miền `-180..180`. | `105.8342` → `105.8342` | `SELECT geo_normalize_longitude(longitude);` |
| Chuẩn hóa GTFS ID | `gtfs_normalize_id` | GTFS identifier preprocessing | Trim/collapse whitespace của ID và reject line break. Không validate foreign key trong GTFS feed. | `  stop_001  ` → `stop_001` | `SELECT gtfs_normalize_id(stop_id);` |

## Dữ liệu khoa học

Đăng ký bằng `register_scientific_udfs(t_env)`.

| Tên hiển thị | SQL function | Chuẩn / mức validation | Mô tả | Giá trị trước → sau | Ví dụ SQL |
| --- | --- | --- | --- | --- | --- |
| Chuẩn hóa hệ tọa độ thiên văn | `astro_normalize_celestial_frame` | Astronomy controlled aliases | Map một số alias phổ biến về `ICRS`, `FK5`, `FK4`, `GALACTIC`... | `galactic` → `GALACTIC` | `SELECT astro_normalize_celestial_frame(frame);` |
| Chuẩn hóa FITS header keyword | `astro_normalize_fits_keyword` | FITS header keyword syntax | Uppercase, bỏ whitespace và giới hạn syntax/độ dài keyword. | `date-obs` → `DATE-OBS` | `SELECT astro_normalize_fits_keyword(keyword);` |
| Chuẩn hóa CF-style standard name | `climate_normalize_cf_standard_name` | CF-style syntax-only | Lowercase và đổi whitespace/hyphen thành underscore. Không lookup CF Standard Name Table. | `Air Temperature` → `air_temperature` | `SELECT climate_normalize_cf_standard_name(variable_name);` |
| Chuẩn hóa GRIB short name | `climate_normalize_grib_short_name` | GRIB short-name syntax-only | Lowercase short-name token. Không lookup parameter table/ecCodes. | `T2M` → `t2m` | `SELECT climate_normalize_grib_short_name(short_name);` |
| Chuẩn hóa chromosome label | `genomics_normalize_chromosome` | Genomics metadata normalization | Bỏ prefix `chr`, uppercase và map mitochondrial `M` → `MT`; vẫn cho phép contig label bảo thủ. | `chrM` → `MT` | `SELECT genomics_normalize_chromosome(chromosome);` |
| Chuẩn hóa DNA sequence | `genomics_normalize_dna_sequence` | IUPAC DNA symbols | Bỏ whitespace, uppercase và validate bộ ký hiệu nucleotide IUPAC được hỗ trợ. | `acgt n` → `ACGTN` | `SELECT genomics_normalize_dna_sequence(sequence);` |
| Chuẩn hóa VCF genotype | `genomics_normalize_vcf_genotype` | VCF genotype syntax | Bỏ whitespace, validate allele token và giữ `/` so với `|` để không mất phased semantics. | `0 / 1` → `0/1` | `SELECT genomics_normalize_vcf_genotype(genotype);` |

## Bảo hiểm / ACORD

Đăng ký bằng `register_insurance_udfs(t_env)`.

| Tên hiển thị | SQL function | Chuẩn / mức validation | Mô tả | Giá trị trước → sau | Ví dụ SQL |
| --- | --- | --- | --- | --- | --- |
| Chuẩn hóa ACORD version | `insurance_normalize_acord_version` | ACORD-oriented syntax cleanup | Bỏ prefix `ACORD`, `v`, separator và giữ version numeric. Không validate schema release cụ thể. | `ACORD v2.0` → `2.0` | `SELECT insurance_normalize_acord_version(acord_version);` |
| Chuẩn hóa coverage code | `insurance_normalize_coverage_code` | Generic insurance code syntax | Uppercase, đổi whitespace thành underscore và kiểm tra character set bảo thủ. | `bodily injury` → `BODILY_INJURY` | `SELECT insurance_normalize_coverage_code(coverage_code);` |
| Chuẩn hóa policy number | `insurance_normalize_policy_number` | Generic policy identifier syntax | Remove whitespace, uppercase và kiểm tra syntax mã hợp đồng bảo hiểm. Không lookup policy trong insurer system. | ` pl-2026 / 001 ` → `PL-2026/001` | `SELECT insurance_normalize_policy_number(policy_no);` |

## Nguyên tắc dùng standards pack

Validator scalar nên dừng ở canonicalization/syntax/checksum. Các phần cần danh mục versioned như FHIR ValueSet, CF Standard Name Table, EPSG registry, BIC directory, ISO 4217 list, DICOM terminology hoặc GTFS relational integrity nên được xử lý bằng parser/validator/reference-data layer chuyên biệt.
