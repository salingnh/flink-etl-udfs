from __future__ import annotations

import importlib
import inspect
import json
import sys
import types

import pytest

from flink_etl_udfs.enrichment import profile


class _FakeResponse:
    def __init__(self, body: dict[str, object], status: int = 200) -> None:
        self._body = json.dumps(body).encode("utf-8")
        self._status = status

    def __enter__(self) -> "_FakeResponse":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        return None

    def getcode(self) -> int:
        return self._status

    def read(self) -> bytes:
        return self._body


def test_extract_profile_url_builds_expected_request(monkeypatch) -> None:
    captured: dict[str, object] = {}
    response_body = {
        "statusCode": 200,
        "message": "POST Request successful.",
        "result": [
            {
                "source_type": 1,
                "actor_id": "100001614198876",
                "actor_username": "sangnv",
                "url": "https://facebook.com/sangnv",
                "domain": "facebook.com",
                "is_social": True,
                "type": "user",
                "platform": "facebook",
                "platform_alias": "facebook.com",
            }
        ],
    }

    def fake_urlopen(http_request, timeout):
        captured["request"] = http_request
        captured["timeout"] = timeout
        return _FakeResponse(response_body)

    monkeypatch.setattr(profile.request, "urlopen", fake_urlopen)

    result = profile.extract_profile_url_sync(
        " https://facebook.com/sangnv ",
        endpoint="http://profile-service.local/extract",
        timeout_seconds=3.0,
    )

    assert result is not None
    parsed_result = json.loads(result)
    assert parsed_result["actor_id"] == "100001614198876"
    assert parsed_result["platform"] == "facebook"

    http_request = captured["request"]
    assert http_request.full_url == "http://profile-service.local/extract"
    assert http_request.get_method() == "POST"
    assert http_request.get_header("Accept") == "text/plain"
    assert http_request.get_header("Content-type") == "application/json-patch+json"
    assert json.loads(http_request.data.decode("utf-8")) == {
        "parse_only": False,
        "parse_display_name": False,
        "sources": ["https://facebook.com/sangnv"],
    }
    assert captured["timeout"] == 3.0


def test_extract_profile_url_rejects_invalid_input_without_calling_api(monkeypatch) -> None:
    def fail_if_called(*args, **kwargs):
        raise AssertionError("urlopen must not be called for invalid profile URL")

    monkeypatch.setattr(profile.request, "urlopen", fail_if_called)

    assert profile.extract_profile_url_sync(None) is None
    assert profile.extract_profile_url_sync("   ") is None
    assert profile.extract_profile_url_sync("facebook.com/sangnv") is None
    assert profile.extract_profile_url_sync("file:///tmp/profile") is None


def test_extract_profile_url_returns_none_for_empty_result(monkeypatch) -> None:
    monkeypatch.setattr(
        profile.request,
        "urlopen",
        lambda *args, **kwargs: _FakeResponse({"statusCode": 200, "result": []}),
    )

    assert (
        profile.extract_profile_url_sync(
            "https://facebook.com/unknown",
            endpoint="http://profile-service.local/extract",
        )
        is None
    )


def test_extract_profile_url_raises_on_service_failure(monkeypatch) -> None:
    monkeypatch.setattr(
        profile.request,
        "urlopen",
        lambda *args, **kwargs: _FakeResponse({"statusCode": 500, "result": []}),
    )

    with pytest.raises(profile.ProfileExtractError, match="statusCode"):
        profile.extract_profile_url_sync(
            "https://facebook.com/sangnv",
            endpoint="http://profile-service.local/extract",
        )


def test_extract_profile_url_sync_is_plain_function() -> None:
    assert callable(profile.extract_profile_url_sync)
    assert profile.extract_profile_url_sync.__name__ == "extract_profile_url_sync"
    assert not inspect.iscoroutinefunction(profile.extract_profile_url_sync)


def test_enrichment_udf_wraps_sync_callable_without_fixed_input_type(monkeypatch) -> None:
    calls: dict[str, object] = {}

    def fake_udf(function, **kwargs):
        calls["function"] = function
        calls["kwargs"] = kwargs
        return {"wrapped": function}

    pyflink_module = types.ModuleType("pyflink")
    table_module = types.ModuleType("pyflink.table")
    udf_module = types.ModuleType("pyflink.table.udf")
    udf_module.udf = fake_udf
    table_module.udf = udf_module
    pyflink_module.table = table_module

    monkeypatch.setitem(sys.modules, "pyflink", pyflink_module)
    monkeypatch.setitem(sys.modules, "pyflink.table", table_module)
    monkeypatch.setitem(sys.modules, "pyflink.table.udf", udf_module)
    sys.modules.pop("flink_etl_udfs.udfs._safe", None)
    sys.modules.pop("flink_etl_udfs.udfs.enrichment", None)

    try:
        module = importlib.import_module("flink_etl_udfs.udfs.enrichment")

        wrapped = calls["function"]
        assert module.extract_profile_url == {"wrapped": wrapped}
        assert getattr(wrapped, "__wrapped__", None) is profile.extract_profile_url_sync
        assert calls["kwargs"] == {
            "result_type": "STRING",
            "deterministic": False,
        }
        assert "input_types" not in calls["kwargs"]
        assert not inspect.iscoroutinefunction(wrapped)
    finally:
        sys.modules.pop("flink_etl_udfs.udfs._safe", None)
        sys.modules.pop("flink_etl_udfs.udfs.enrichment", None)
