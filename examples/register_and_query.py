"""Minimal example: register library UDFs and call them from Flink SQL."""

from pyflink.table import EnvironmentSettings, TableEnvironment

from flink_etl_udfs.registry import register_default_udfs

settings = EnvironmentSettings.in_streaming_mode()
t_env = TableEnvironment.create(settings)
register_default_udfs(t_env)

result = t_env.sql_query(
    """
    SELECT
        mask_text('0912345678') AS masked,
        sha256_fingerprint('customer-001') AS fingerprint,
        normalize_ip('2001:0db8:0:0:0:0:0:1') AS ip
    """
)

result.execute().print()
