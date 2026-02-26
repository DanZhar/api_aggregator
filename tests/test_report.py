"""Тесты формирования отчётов."""

import json
from datetime import datetime

import pytest

from api_aggregator.models import AggregatedReport, FetchResult
from api_aggregator.report import generate_json_report, generate_text_report, save_report


@pytest.fixture
def sample_report():
    return AggregatedReport(
        timestamp=datetime(2025, 1, 15, 14, 30, 0),
        total_sources=2,
        successful=1,
        failed=1,
        total_time_ms=1070.0,
        results=[
            FetchResult(
                source_name="weather",
                success=True,
                data={"temperature": 15.2, "wind": 4.5},
                status_code=200,
                elapsed_ms=320.0,
            ),
            FetchResult(
                source_name="catfact",
                success=False,
                error="Timeout after 10s",
                elapsed_ms=750.0,
                retries_used=3,
            ),
        ],
    )


class TestGenerateTextReport:
    def test_contains_header(self, sample_report):
        text = generate_text_report(sample_report)
        assert "API Aggregator Report" in text

    def test_contains_timestamp(self, sample_report):
        text = generate_text_report(sample_report)
        assert "2025" in text

    def test_contains_sources_summary(self, sample_report):
        text = generate_text_report(sample_report)
        assert "2 total" in text
        assert "1 successful" in text
        assert "1 failed" in text

    def test_contains_total_time(self, sample_report):
        text = generate_text_report(sample_report)
        assert "1070" in text

    def test_successful_source_shows_ok(self, sample_report):
        text = generate_text_report(sample_report)
        assert "weather" in text
        assert "OK" in text

    def test_successful_source_shows_data(self, sample_report):
        text = generate_text_report(sample_report)
        assert "temperature" in text
        assert "15.2" in text

    def test_failed_source_shows_failed(self, sample_report):
        text = generate_text_report(sample_report)
        assert "FAILED" in text

    def test_failed_source_shows_error(self, sample_report):
        text = generate_text_report(sample_report)
        assert "Timeout" in text

    def test_returns_string(self, sample_report):
        assert isinstance(generate_text_report(sample_report), str)


class TestGenerateJsonReport:
    def test_valid_json(self, sample_report):
        result = generate_json_report(sample_report)
        data = json.loads(result)
        assert isinstance(data, dict)

    def test_has_required_keys(self, sample_report):
        result = generate_json_report(sample_report)
        data = json.loads(result)
        assert "timestamp" in data
        assert "total_sources" in data
        assert "successful" in data
        assert "failed" in data
        assert "total_time_ms" in data
        assert "results" in data

    def test_values(self, sample_report):
        result = generate_json_report(sample_report)
        data = json.loads(result)
        assert data["total_sources"] == 2
        assert data["successful"] == 1
        assert data["failed"] == 1

    def test_results_list(self, sample_report):
        result = generate_json_report(sample_report)
        data = json.loads(result)
        assert len(data["results"]) == 2
        assert data["results"][0]["source_name"] == "weather"
        assert data["results"][0]["success"] is True
        assert data["results"][1]["success"] is False

    def test_returns_string(self, sample_report):
        assert isinstance(generate_json_report(sample_report), str)


class TestSaveReport:
    def test_saves_to_file(self, tmp_path):
        filepath = str(tmp_path / "report.txt")
        save_report("test content", filepath)
        with open(filepath) as f:
            assert f.read() == "test content"

    def test_creates_file(self, tmp_path):
        filepath = str(tmp_path / "new_report.txt")
        save_report("data", filepath)
        assert (tmp_path / "new_report.txt").exists()
