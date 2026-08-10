"""Example: combine OSINT-specific and generic internet/security UDF packs."""

from pyflink.table import EnvironmentSettings, TableEnvironment

from flink_etl_udfs.registry import (
    register_common_udfs,
    register_internet_udfs,
    register_osint_udfs,
    register_security_udfs,
)

settings = EnvironmentSettings.in_streaming_mode()
t_env = TableEnvironment.create(settings)
register_common_udfs(t_env)
register_internet_udfs(t_env)
register_security_udfs(t_env)
register_osint_udfs(t_env)

result = t_env.sql_query(
    """
    SELECT
        osint_normalize_username('@@Analyst.User') AS username,
        net_normalize_domain('BÜCHER.DE.') AS domain_name,
        net_normalize_asn('as13335') AS asn,
        security_normalize_cve('cve 2024 12345') AS cve,
        etl_normalize_probability('0.82') AS confidence
    """
)

result.execute().print()
