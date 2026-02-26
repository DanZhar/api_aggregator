"""Тесты Pydantic-моделей."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from api_aggregator.models import AggregatedReport, AppConfig, FetchResult, SourceConfig


class TestSourceConfig:
    def test_valid_source(self):
        s = SourceConfig(
            name="test",
            url="https://example.com/api",
            response_mapping={"key": "path"},
        )
        assert s.name == "test"
        assert s.method == "GET"
        assert s.params == {}
        assert s.headers == {}

    def test_all_fields(self):
        s = SourceConfig(
            name="full",
            url="https://example.com",
            params={"q": "test"},
            method="POST",
            headers={"Authorization": "Bearer xxx"},
            response_mapping={"data": "result.data"},
        )
        assert s.method == "POST"
        assert s.headers["Authorization"] == "Bearer xxx"

    def test_missing_name_raises(self):
        with pytest.raises(ValidationError):
            SourceConfig(url="https://x.com", response_mapping={"a": "b"})

    def test_missing_url_raises(self):
        with pytest.raises(ValidationError):
            SourceConfig(name="test", response_mapping={"a": "b"})

    def test_missing_mapping_raises(self):
        with pytest.raises(ValidationError):
            SourceConfig(name="test", url="https://x.com")


class TestAppConfig:
    def test_valid_config(self, sample_sources):
        config = AppConfig(sources=sample_sources)
        assert len(config.sources) == 2

    def test_empty_sources(self):
        config = AppConfig(sources=[])
        assert config.sources == []

    def test_invalid_source_raises(self):
        with pytest.raises(ValidationError):
            AppConfig(sources=[{"name": "bad"}])


class TestFetchResult:
    def test_successful_result(self):
        r = FetchResult(
            source_name="test",
            success=True,
            data={"key": "value"},
            status_code=200,
            elapsed_ms=100.0,
        )
        assert r.success is True
        assert r.error is None
        assert r.retries_used == 0

    def test_failed_result(self):
        r = FetchResult(
            source_name="test",
            success=False,
            error="Connection refused",
            elapsed_ms=50.0,
            retries_used=3,
        )
        assert r.success is False
        assert r.data is None
        assert r.retries_used == 3

    def test_defaults(self):
        r = FetchResult(source_name="x", success=True)
        assert r.data is None
        assert r.status_code is None
        assert r.elapsed_ms == 0.0
        assert r.retries_used == 0


class TestAggregatedReport:
    def test_valid_report(self, sample_results):
        report = AggregatedReport(
            timestamp=datetime.now(),
            total_sources=2,
            successful=1,
            failed=1,
            total_time_ms=1070.0,
            results=sample_results,
        )
        assert report.total_sources == 2
        assert len(report.results) == 2

    def test_serialization(self, sample_results):
        report = AggregatedReport(
            timestamp=datetime(2025, 1, 15, 14, 30, 0),
            total_sources=2,
            successful=1,
            failed=1,
            total_time_ms=1070.0,
            results=sample_results,
        )
        data = report.model_dump()
        assert data["total_sources"] == 2
        assert isinstance(data["results"], list)

    def test_json_serialization(self, sample_results):
        report = AggregatedReport(
            timestamp=datetime(2025, 1, 15, 14, 30, 0),
            total_sources=2,
            successful=1,
            failed=1,
            total_time_ms=1070.0,
            results=sample_results,
        )
        json_str = report.model_dump_json()
        assert "total_sources" in json_str
        assert "weather" in json_str
