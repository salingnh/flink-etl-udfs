"""Minimal example: register the OSINT domain pack and call it from Flink SQL."""

from pyflink.table import EnvironmentSettings, TableEnvironment

from flink_etl_udfs.registry import register_osint_udfs

settings = EnvironmentSettings.in_streaming_mode()
t_env = TableEnvironment.create(settings)
register_osint_udfs(t_env)

result = t_env.sql_query(
    """
    SELECT
        osint_normalize_username('@@Analyst.User') AS username,
        osint_normalize_domain('BÜCHER.DE.') AS domain,
        osint_normalize_asn('as13335') AS asn,
        osint_normalize_cve('cve 2024 12345') AS cve,
        osint_normalize_confidence('0.82') AS confidence
    """
)

result.execute().print()
