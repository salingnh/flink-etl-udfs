# Chuẩn quốc tế và domain chuyên ngành

File này chỉ giữ scalar UDF có semantics chuẩn/ngành đủ rõ. Các format cần parser đầy đủ như ACORD XML, NetCDF/GRIB, FITS/WCS, VCF/BCF/BAM... được để ở parser/enrichment layer thay vì scalar UDF.

## Y tế: FHIR / HL7 v2 / DICOM

Đăng ký bằng `register_healthcare_udfs(t_env)`.

| Tên hiển thị | SQL function | Chuẩn / mức validation | Mô tả | Giá trị trước → sau | Ví dụ SQL |
| --- | --- | --- | --- | --- | --- |
| Chuẩn hóa DICOM UID | `health_normalize_dicom_uid` | DICOM UID/OID syntax | Validate numeric-dot UID và giới hạn 64 ký tự. | `1.2.840.10008.1.2.1` → `1.2.840.10008.1.2.1` | `SELECT health_normalize_dicom_uid(study_uid);` |
| Kiểm tra FHIR Resource ID | `health_normalize_fhir_id` | FHIR id syntax | Validate charset/length của FHIR resource id. | `patient-001` → `patient-001` | `SELECT health_normalize_fhir_id(resource_id);` |
| Chuẩn hóa FHIR Reference | `health_normalize_fhir_reference` | FHIR local/relative reference | Validate `ResourceType/id` hoặc `#contained-id`; không resolve qua server. | `Patient/patient-001` → `Patient/patient-001` | `SELECT health_normalize_fhir_reference(subject_ref);` |
| Chuẩn hóa HL7 v2 Message Type | `health_normalize_hl7_message_type` | HL7 v2 syntax | Uppercase, normalize separator và kiểm tra dạng như `ADT^A01`. | `adt~a01` → `ADT^A01` | `SELECT health_normalize_hl7_message_type(message_type);` |

## Tài chính / định danh pháp nhân

Đăng ký bằng `register_finance_udfs(t_env)`.

| Tên hiển thị | SQL function | Chuẩn / mức validation | Mô tả | Giá trị trước → sau | Ví dụ SQL |
| --- | --- | --- | --- | --- | --- |
| Chuẩn hóa BIC | `finance_normalize_bic` | ISO 9362 syntax | Remove whitespace, uppercase và validate cấu trúc BIC 8/11 ký tự. | `deut de ff` → `DEUTDEFF` | `SELECT finance_normalize_bic(bic);` |
| Chuẩn hóa IBAN | `finance_normalize_iban` | ISO 13616 + mod-97 | Remove whitespace, uppercase và kiểm tra mod-97. | `GB82 WEST 1234 5698 7654 32` → `GB82WEST12345698765432` | `SELECT finance_normalize_iban(iban);` |
| Chuẩn hóa ISO 20022 message type | `finance_normalize_iso20022_message_type` | ISO 20022 identifier | Lowercase và normalize `_` thành `.`. | `PACS_008_001_08` → `pacs.008.001.08` | `SELECT finance_normalize_iso20022_message_type(message_type);` |
| Chuẩn hóa LEI | `finance_normalize_lei` | ISO 17442 + mod-97 | Uppercase, validate 20 ký tự và kiểm tra mod-97. | `5493001KJTIIGC8Y1R12` → `5493001KJTIIGC8Y1R12` | `SELECT finance_normalize_lei(lei);` |

## Supply chain / GS1 / EPCIS

Đăng ký bằng `register_supply_chain_udfs(t_env)`.

| Tên hiển thị | SQL function | Chuẩn / mức validation | Mô tả | Giá trị trước → sau | Ví dụ SQL |
| --- | --- | --- | --- | --- | --- |
| Chuẩn hóa EPCIS event type | `supply_normalize_epcis_event_type` | GS1 EPCIS | Map alias về canonical event class. | `object_event` → `ObjectEvent` | `SELECT supply_normalize_epcis_event_type(event_type);` |
| Chuẩn hóa GTIN | `supply_normalize_gtin` | GS1 GTIN + check digit | Bỏ separator, nhận GTIN-8/12/13/14 và kiểm tra check digit. | `4006 3813 3393 1` → `4006381333931` | `SELECT supply_normalize_gtin(gtin);` |
| Chuẩn hóa SSCC | `supply_normalize_sscc` | GS1 SSCC + check digit | Bỏ separator, yêu cầu 18 chữ số và kiểm tra check digit. | `123456789012345675` → `123456789012345675` | `SELECT supply_normalize_sscc(sscc);` |

## Industrial / IoT

Đăng ký bằng `register_industrial_udfs(t_env)`.

| Tên hiển thị | SQL function | Chuẩn / mức validation | Mô tả | Giá trị trước → sau | Ví dụ SQL |
| --- | --- | --- | --- | --- | --- |
| Chuẩn hóa OBIS code | `iot_normalize_obis_code` | DLMS/COSEM OBIS syntax | Normalize `A-B:C.D.E*F`; semantic catalogue nằm ở reference layer. | `1-0:1.8.0*255` → `1-0:1.8.0*255` | `SELECT iot_normalize_obis_code(obis_code);` |
| Chuẩn hóa OPC UA NodeId | `iot_normalize_opcua_node_id` | OPC UA NodeId syntax | Canonicalize namespace và identifier-type prefix. | `NS=2;S=Temperature` → `ns=2;s=Temperature` | `SELECT iot_normalize_opcua_node_id(node_id);` |

## Geospatial

Đăng ký bằng `register_geospatial_udfs(t_env)`.

| Tên hiển thị | SQL function | Chuẩn / mức validation | Mô tả | Giá trị trước → sau | Ví dụ SQL |
| --- | --- | --- | --- | --- | --- |
| Chuẩn hóa EPSG CRS code | `geo_normalize_epsg_code` | EPSG identifier shape | Chuẩn hóa numeric CRS identifier về `EPSG:<code>`; registry membership cần lookup. | `epsg:4326` → `EPSG:4326` | `SELECT geo_normalize_epsg_code(crs);` |
| Chuẩn hóa latitude | `geo_normalize_latitude` | Coordinate range | Parse float và chấp nhận miền `-90..90`. | `21.0278` → `21.0278` | `SELECT geo_normalize_latitude(latitude);` |
| Chuẩn hóa longitude | `geo_normalize_longitude` | Coordinate range | Parse float và chấp nhận miền `-180..180`. | `105.8342` → `105.8342` | `SELECT geo_normalize_longitude(longitude);` |
