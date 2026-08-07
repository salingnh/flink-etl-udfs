from flink_etl_udfs.core.osint_web import (
    canonicalize_url_value,
    extract_url_host_value,
    normalize_domain_value,
    normalize_profile_url_value,
    redact_url_secrets_value,
)


def test_normalize_domain_idna_and_case() -> None:
    assert normalize_domain_value("BÜCHER.DE.") == "xn--bcher-kva.de"


def test_canonicalize_url_removes_tracking_fragment_and_userinfo() -> None:
    value = "HTTPS://user:pass@Example.COM:443/a?utm_source=x&b=2&a=1#section"
    assert canonicalize_url_value(value) == "https://example.com/a?a=1&b=2"


def test_profile_url_drops_query_state() -> None:
    assert normalize_profile_url_value("https://example.com/u/name?view=1") == (
        "https://example.com/u/name"
    )


def test_extract_url_host() -> None:
    assert extract_url_host_value("https://WWW.Example.com/path") == "www.example.com"


def test_redact_url_secrets() -> None:
    result = redact_url_secrets_value(
        "https://user:pass@example.com/api?token=abc&query=osint"
    )
    assert result == "https://example.com/api?token=%5BREDACTED%5D&query=osint"
