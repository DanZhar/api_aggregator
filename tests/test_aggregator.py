"""Тесты агрегации результатов."""

from datetime import datetime

from api_aggregator.aggregator import aggregate
from api_aggregator.models import AggregatedReport, FetchResult


class TestAggregate:
    def test_returns_aggregated_report(self, sample_results):
        report = aggregate(sample_results)
        assert isinstance(report, AggregatedReport)

    def test_total_sources(self, sample_results):
        report = aggregate(sample_results)
        assert report.total_sources == 2

    def test_successful_count(self, sample_results):
        report = aggregate(sample_results)
        assert report.successful == 1

    def test_failed_count(self, sample_results):
        report = aggregate(sample_results)
        assert report.failed == 1

    def test_total_time(self, sample_results):
        report = aggregate(sample_results)
        # 320.0 + 750.0 = 1070.0
        assert report.total_time_ms == 1070.0

    def test_has_timestamp(self, sample_results):
        report = aggregate(sample_results)
        assert isinstance(report.timestamp, datetime)

    def test_results_preserved(self, sample_results):
        report = aggregate(sample_results)
        assert len(report.results) == 2

    def test_empty_results(self):
        report = aggregate([])
        assert report.total_sources == 0
        assert report.successful == 0
        assert report.failed == 0
        assert report.total_time_ms == 0.0

    def test_all_successful(self):
        results = [
            FetchResult(source_name="a", success=True, elapsed_ms=100),
            FetchResult(source_name="b", success=True, elapsed_ms=200),
        ]
        report = aggregate(results)
        assert report.successful == 2
        assert report.failed == 0

    def test_all_failed(self):
        results = [
            FetchResult(source_name="a", success=False, elapsed_ms=100, error="err"),
            FetchResult(source_name="b", success=False, elapsed_ms=200, error="err"),
        ]
        report = aggregate(results)
        assert report.successful == 0
        assert report.failed == 2
