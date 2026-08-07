from flink_etl_udfs.core.network import normalize_cidr_value, normalize_ip_value


def test_normalize_ipv6() -> None:
    assert normalize_ip_value("2001:0db8:0:0:0:0:0:1") == "2001:db8::1"


def test_invalid_ip_returns_null() -> None:
    assert normalize_ip_value("999.999.1.1") is None


def test_normalize_cidr_clears_host_bits() -> None:
    assert normalize_cidr_value("192.168.1.14/24") == "192.168.1.0/24"
