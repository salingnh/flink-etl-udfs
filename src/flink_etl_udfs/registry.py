"""Central registration helper for PyFlink TableEnvironment."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyflink.table import TableEnvironment


def register_default_udfs(table_env: "TableEnvironment") -> None:
    """Register the stable default UDF set under predictable SQL names."""
    from flink_etl_udfs.udfs.identifiers import digits_only, normalize_email
    from flink_etl_udfs.udfs.network import normalize_cidr, normalize_ip
    from flink_etl_udfs.udfs.privacy import mask_email, mask_text, sha256_fingerprint
    from flink_etl_udfs.udfs.text import (
        normalize_unicode_nfc,
        normalize_whitespace,
        null_if_blank,
        trim_text,
    )

    functions = {
        "digits_only": digits_only,
        "mask_email": mask_email,
        "mask_text": mask_text,
        "normalize_cidr": normalize_cidr,
        "normalize_email": normalize_email,
        "normalize_ip": normalize_ip,
        "normalize_unicode_nfc": normalize_unicode_nfc,
        "normalize_whitespace": normalize_whitespace,
        "null_if_blank": null_if_blank,
        "sha256_fingerprint": sha256_fingerprint,
        "trim_text": trim_text,
    }

    for name, function in functions.items():
        table_env.create_temporary_system_function(name, function)


__all__ = ["register_default_udfs"]
