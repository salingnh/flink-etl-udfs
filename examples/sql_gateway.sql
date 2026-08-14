-- Build/upload dist/flink_etl_udfs.zip first.
SET 'python.files' = 's3://fusion_center/transform-library/flink_etl_udfs.zip';

CREATE TEMPORARY SYSTEM FUNCTION ISO2108_NORMALIZE_ISBN13
AS 'flink_etl_udfs.udfs.standards.iso2108_normalize_isbn13'
LANGUAGE PYTHON;

CREATE TEMPORARY SYSTEM FUNCTION RFC9562_NORMALIZE_UUID
AS 'flink_etl_udfs.udfs.standards.rfc9562_normalize_uuid'
LANGUAGE PYTHON;

CREATE TEMPORARY SYSTEM FUNCTION ISO3166_NORMALIZE_ALPHA3
AS 'flink_etl_udfs.udfs.standards.iso3166_normalize_alpha3'
LANGUAGE PYTHON;

CREATE TEMPORARY SYSTEM FUNCTION VN_NORMALIZE_MOBILE_PHONE
AS 'flink_etl_udfs.udfs.vietnam.normalize_vn_mobile_phone'
LANGUAGE PYTHON;

SELECT
    ISO2108_NORMALIZE_ISBN13('0-306-40615-2') AS isbn13,
    RFC9562_NORMALIZE_UUID('550E8400-E29B-41D4-A716-446655440000') AS uuid_norm,
    ISO3166_NORMALIZE_ALPHA3('VN') AS country_alpha3,
    VN_NORMALIZE_MOBILE_PHONE('0169 123 4567') AS phone_vn;
