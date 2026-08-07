"""Register researched P0-P3 domain packs and exercise representative SQL functions."""

from pyflink.table import EnvironmentSettings, TableEnvironment

from flink_etl_udfs.registry import register_all_udfs

settings = EnvironmentSettings.in_streaming_mode()
t_env = TableEnvironment.create(settings)
register_all_udfs(t_env)

result = t_env.sql_query(
    """
    SELECT
        etl_normalize_iso_datetime('2026-08-07T09:00:00+07:00') AS ts_utc,
        vn_normalize_phone('0983132288') AS vn_phone,
        finance_normalize_iban('GB82 WEST 1234 5698 7654 32') AS iban,
        health_normalize_fhir_reference('Patient/patient-001') AS fhir_ref,
        supply_normalize_gtin('4006381333931') AS gtin,
        iot_normalize_opcua_node_id('ns=2;s=Temperature') AS node_id,
        geo_normalize_epsg_code('epsg:4326') AS crs,
        genomics_normalize_chromosome('chrM') AS chromosome
    """
)

result.execute().print()
