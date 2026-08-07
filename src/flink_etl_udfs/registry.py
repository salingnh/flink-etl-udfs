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


def register_osint_udfs(table_env: "TableEnvironment") -> None:
    """Register the OSINT domain UDF pack under predictable SQL names."""
    from flink_etl_udfs.udfs import osint

    functions = {
        "osint_build_observation_id": osint.build_observation_id,
        "osint_canonicalize_url": osint.canonicalize_url,
        "osint_classify_account_identifier": osint.classify_account_identifier,
        "osint_classify_git_object_hash": osint.classify_git_object_hash,
        "osint_classify_hash_type": osint.classify_hash_type,
        "osint_content_sha256": osint.content_sha256,
        "osint_extract_url_host": osint.extract_url_host,
        "osint_normalize_asn": osint.normalize_asn,
        "osint_normalize_confidence": osint.normalize_confidence,
        "osint_normalize_cve": osint.normalize_cve,
        "osint_normalize_dns_record_type": osint.normalize_dns_record_type,
        "osint_normalize_domain": osint.normalize_domain,
        "osint_normalize_entity_type": osint.normalize_entity_type,
        "osint_normalize_exposure_status": osint.normalize_exposure_status,
        "osint_normalize_git_object_id": osint.normalize_git_object_id,
        "osint_normalize_hex_hash": osint.normalize_hex_hash,
        "osint_normalize_lei": osint.normalize_lei,
        "osint_normalize_mime_type": osint.normalize_mime_type,
        "osint_normalize_name_search_key": osint.normalize_name_search_key,
        "osint_normalize_observed_at_utc": osint.normalize_observed_at_utc,
        "osint_normalize_ownership_percentage": osint.normalize_ownership_percentage,
        "osint_normalize_platform": osint.normalize_platform,
        "osint_normalize_profile_url": osint.normalize_profile_url,
        "osint_normalize_repository_url": osint.normalize_repository_url,
        "osint_normalize_username": osint.normalize_username,
        "osint_normalize_verification_status": osint.normalize_verification_status,
        "osint_redact_url_secrets": osint.redact_url_secrets,
    }

    for name, function in functions.items():
        table_env.create_temporary_system_function(name, function)


__all__ = ["register_default_udfs", "register_osint_udfs"]
