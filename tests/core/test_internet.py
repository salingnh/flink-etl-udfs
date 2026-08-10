from flink_etl_udfs.core.internet import (
    canonicalize_url_value,
    extract_url_host_value,
    normalize_asn_value,
    normalize_dns_record_type_value,
    normalize_domain_value,
    normalize_mime_type_value,
    redact_url_secrets_value,
)


def test_normalize_domain_idna_and_case() -> None:
    assert normalize_domain_value("BÜCHER.DE.") == "xn--bcher-kva.de"


def test_canonicalize_url_removes_tracking_fragment_and_userinfo() -> None:
    value = "HTTPS://user:pass@Example.COM:443/a?utm_source=x&b=2&a=1#section"
    assert canonicalize_url_value(value) == "https://example.com/a?a=1&b=2"


def test_extract_url_host() -> None:
    assert extract_url_host_value("https://WWW.Example.com/path") == "www.example.com"


def test_redact_url_secrets() -> None:
    result = redact_url_secrets_value(
        "https://user:pass@example.com/api?token=abc&query=data"
    )
    assert result == "https://example.com/api?token=%5BREDACTED%5D&query=data"


def test_normalize_asn() -> None:
    assert normalize_asn_value(" as13335 ") == "AS13335"
    assert normalize_asn_value("not-asn") is None


def test_dns_record_type_is_controlled() -> None:
    assert normalize_dns_record_type_value("aaaa") == "AAAA"
    assert normalize_dns_record_type_value("BOGUS") is None


def test_normalize_mime_type_drops_parameters() -> None:
    assert normalize_mime_type_value("Text/HTML; charset=UTF-8") == "text/html"
    assert normalize_mime_type_value("invalid") is None
