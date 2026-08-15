from flink_etl_udfs.core.identity_standards import (
    build_icao9303_document_id_value,
    build_iso18013_driving_licence_id_value,
    build_iso18013_mdl_id_value,
    build_iso23220_eid_id_value,
    build_oidc_subject_key_value,
    normalize_activitystreams_id_value,
    normalize_iso2108_isbn13_value,
    normalize_iso3166_alpha3_value,
    normalize_iso3297_issn_value,
    normalize_iso26324_doi_value,
    normalize_rfc3986_uri_value,
    normalize_rfc8141_urn_value,
    normalize_rfc9562_uuid_value,
    normalize_w3c_did_value,
)


def test_document_and_mobile_identity_keys() -> None:
    assert build_icao9303_document_id_value("vnm", " B1234567 ") == "VNM:B1234567"
    assert (
        build_iso18013_driving_licence_id_value("VN", "C06", "12345678901")
        == "VNM:C06:12345678901"
    )
    assert (
        build_iso18013_mdl_id_value("https://issuer.example", "mDL-123")
        == "mdl:https%3A%2F%2Fissuer.example:mDL-123"
    )
    assert (
        build_iso23220_eid_id_value(
            "https://id.example", "national-eid", "123456789"
        )
        == "eid:https%3A%2F%2Fid.example:national-eid:123456789"
    )


def test_iso3166_alpha3_reference_lookup() -> None:
    assert normalize_iso3166_alpha3_value("vn") == "VNM"
    assert normalize_iso3166_alpha3_value("US") == "USA"
    assert normalize_iso3166_alpha3_value("VNM") == "VNM"
    assert normalize_iso3166_alpha3_value("ZZ") is None


def test_oidc_and_activitystreams_identifiers() -> None:
    assert (
        build_oidc_subject_key_value("https://accounts.example.com", "User-123")
        == "oidc:https%3A%2F%2Faccounts.example.com:User-123"
    )
    assert (
        normalize_activitystreams_id_value(" https://social.example/posts/123 ")
        == "https://social.example/posts/123"
    )
    assert normalize_activitystreams_id_value("/posts/123") is None


def test_rfc_identifier_normalization() -> None:
    assert (
        normalize_rfc3986_uri_value("HTTP://Example.COM/a/%7euser?x=1#Top")
        == "http://example.com/a/~user?x=1#Top"
    )
    assert (
        normalize_rfc9562_uuid_value("550E8400-E29B-41D4-A716-446655440000")
        == "550e8400-e29b-41d4-a716-446655440000"
    )
    assert normalize_rfc9562_uuid_value("not-a-uuid") is None
    assert normalize_rfc8141_urn_value("URN:EXAMPLE:a123%2cz456") == "urn:example:a123%2Cz456"


def test_publication_identifiers() -> None:
    assert normalize_iso26324_doi_value("https://doi.org/10.1000/ABC123") == "10.1000/abc123"
    assert normalize_iso3297_issn_value("ISSN 2049 3630") == "2049-3630"
    assert normalize_iso3297_issn_value("2049-3631") is None
    assert normalize_iso2108_isbn13_value("0-306-40615-2") == "9780306406157"
    assert normalize_iso2108_isbn13_value("978-0-306-40615-7") == "9780306406157"


def test_w3c_did_generic_normalization() -> None:
    assert normalize_w3c_did_value("DID:WEB:example.com:user:123") == "did:web:example.com:user:123"
    assert normalize_w3c_did_value("did:web:") is None
