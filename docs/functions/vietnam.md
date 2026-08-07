# Vietnam / Citizen / Education / Banking Functions

## Vietnam / citizen / education / banking

Register with `register_vietnam_udfs(t_env)`.

| SQL function | Signature | Description | Example |
| --- | --- | --- | --- |
| `vn_build_entity_blocking_key` | `vn_build_entity_blocking_key(name, phone, email) → STRING` | Build readable blocking key from available normalized name/phone/email features. | `SELECT vn_build_entity_blocking_key(full_name, phone, email);` |
| `vn_classify_identity_id` | `vn_classify_identity_id(value) → STRING` | Classify structurally valid 9-digit CMND vs 12-digit CCCD by length. | `SELECT vn_classify_identity_id(identity_no);` |
| `vn_classify_tax_id` | `vn_classify_tax_id(value) → STRING` | Classify normalized VN tax ID as enterprise or dependent_unit. | `SELECT vn_classify_tax_id(mst);` |
| `vn_normalize_academic_year` | `vn_normalize_academic_year(value) → STRING` | Normalize school year such as 2025/26 to 2025-2026. | `SELECT vn_normalize_academic_year(school_year);` |
| `vn_normalize_address` | `vn_normalize_address(value) → STRING` | Normalize Unicode/whitespace/separators in Vietnamese free-text address without guessing admin codes. | `SELECT vn_normalize_address(address);` |
| `vn_normalize_bank_account` | `vn_normalize_bank_account(value) → STRING` | Remove common separators and uppercase alphanumeric bank-account identifier. | `SELECT vn_normalize_bank_account(account_no);` |
| `vn_normalize_citizen_id` | `vn_normalize_citizen_id(value) → STRING` | Keep digits and validate 9/12-digit CMND/CCCD structural shape. | `SELECT vn_normalize_citizen_id(cccd);` |
| `vn_normalize_name` | `vn_normalize_name(value) → STRING` | NFC + whitespace normalization for Vietnamese personal names while preserving case. | `SELECT vn_normalize_name(full_name);` |
| `vn_normalize_phone` | `vn_normalize_phone(value) → STRING` | Normalize Vietnamese phone shape to E.164 using +84. | `SELECT vn_normalize_phone('0912345678');` |
| `vn_normalize_school_code` | `vn_normalize_school_code(value) → STRING` | Normalize school code to uppercase compact allowed-character syntax. | `SELECT vn_normalize_school_code(ma_truong);` |
| `vn_normalize_sms_brandname` | `vn_normalize_sms_brandname(value) → STRING` | Remove whitespace and uppercase SMS sender brand name. | `SELECT vn_normalize_sms_brandname(brandname);` |
| `vn_normalize_student_code` | `vn_normalize_student_code(value) → STRING` | Normalize student code to uppercase compact allowed-character syntax. | `SELECT vn_normalize_student_code(ma_hoc_sinh);` |
| `vn_normalize_tax_id` | `vn_normalize_tax_id(value) → STRING` | Normalize VN tax ID to 10 digits or 10digits-3digits structural form. | `SELECT vn_normalize_tax_id(mst);` |
| `vn_normalize_teacher_code` | `vn_normalize_teacher_code(value) → STRING` | Normalize teacher code to uppercase compact allowed-character syntax. | `SELECT vn_normalize_teacher_code(ma_giao_vien);` |
| `vn_name_search_key` | `vn_name_search_key(value) → STRING` | Build accent-insensitive lowercase blocking/search key for Vietnamese names. | `SELECT vn_name_search_key(full_name);` |
