"""Register curated domain packs and exercise representative SQL functions."""

from pyflink.table import EnvironmentSettings, TableEnvironment

from flink_etl_udfs.registry import register_all_udfs

settings = EnvironmentSettings.in_streaming_mode()
t_env = TableEnvironment.create(settings)
register_all_udfs(t_env)

result = t_env.sql_query(
    """
    SELECT
        etl_normalize_iso_datetime('2026-08-10T09:00:00+07:00') AS ts_utc,
        etl_normalize_e164('0983132288', '+84') AS phone_e164,
        vn_normalize_tax_id('0101234567001') AS tax_id,
        net_normalize_domain('BÜCHER.DE.') AS domain_name,
        security_normalize_cve('cve 2024 12345') AS cve_id,
        finance_normalize_iban('GB82 WEST 1234 5698 7654 32') AS iban,
        health_normalize_fhir_reference('Patient/patient-001') AS fhir_ref,
        supply_normalize_gtin('4006381333931') AS gtin,
        iot_normalize_opcua_node_id('ns=2;s=Temperature') AS node_id,
        geo_normalize_epsg_code('epsg:4326') AS crs
    """
)

result.execute().print()
