"""Тесты асинхронных запросов (fetcher)."""

import asyncio

import pytest
from aioresponses import aioresponses

from api_aggregator.fetcher import RETRYABLE_STATUSES, fetch_all, fetch_source
from api_aggregator.models import FetchResult, SourceConfig


@pytest.fixture
def simple_source():
    return SourceConfig(
        name="test_api",
        url="https://api.example.com/data",
        params={"key": "value"},
        method="GET",
        headers={},
        response_mapping={"result": "data.value"},
    )


# ── fetch_source ─────────────────────────────────────────────────


class TestFetchSource:
    @pytest.mark.asyncio
    async def test_successful_fetch(self, simple_source):
        with aioresponses() as mocked:
            mocked.get(
                "https://api.example.com/data",
                payload={"data": {"value": 42}},
                status=200,
            )
            import aiohttp

            async with aiohttp.ClientSession() as session:
                sem = asyncio.Semaphore(5)
                result = await fetch_source(session, simple_source, sem, timeout=10, retries=3)

            assert isinstance(result, FetchResult)
            assert result.success is True
            assert result.source_name == "test_api"
            assert result.status_code == 200
            assert result.data is not None
            assert result.data["result"] == 42

    @pytest.mark.asyncio
    async def test_returns_fetch_result(self, simple_source):
        with aioresponses() as mocked:
            mocked.get("https://api.example.com/data", payload={"data": {"value": 1}})
            import aiohttp

            async with aiohttp.ClientSession() as session:
                sem = asyncio.Semaphore(5)
                result = await fetch_source(session, simple_source, sem)

            assert isinstance(result, FetchResult)

    @pytest.mark.asyncio
    async def test_failed_fetch_returns_error(self, simple_source):
        with aioresponses() as mocked:
            mocked.get("https://api.example.com/data", status=500)
            mocked.get("https://api.example.com/data", status=500)
            mocked.get("https://api.example.com/data", status=500)
            mocked.get("https://api.example.com/data", status=500)
            import aiohttp

            async with aiohttp.ClientSession() as session:
                sem = asyncio.Semaphore(5)
                result = await fetch_source(session, simple_source, sem, timeout=10, retries=3)

            assert result.success is False
            assert result.error is not None

    @pytest.mark.asyncio
    async def test_timeout_handling(self, simple_source):
        with aioresponses() as mocked:
            mocked.get("https://api.example.com/data", exception=asyncio.TimeoutError())
            mocked.get("https://api.example.com/data", exception=asyncio.TimeoutError())
            mocked.get("https://api.example.com/data", exception=asyncio.TimeoutError())
            mocked.get("https://api.example.com/data", exception=asyncio.TimeoutError())
            import aiohttp

            async with aiohttp.ClientSession() as session:
                sem = asyncio.Semaphore(5)
                result = await fetch_source(session, simple_source, sem, timeout=1, retries=3)

            assert result.success is False

    @pytest.mark.asyncio
    async def test_retries_used_counted(self, simple_source):
        with aioresponses() as mocked:
            mocked.get("https://api.example.com/data", status=500)
            mocked.get("https://api.example.com/data", status=500)
            mocked.get("https://api.example.com/data", payload={"data": {"value": 1}}, status=200)
            import aiohttp

            async with aiohttp.ClientSession() as session:
                sem = asyncio.Semaphore(5)
                result = await fetch_source(session, simple_source, sem, timeout=10, retries=3)

            assert result.success is True
            assert result.retries_used == 2

    @pytest.mark.asyncio
    async def test_elapsed_ms_positive(self, simple_source):
        with aioresponses() as mocked:
            mocked.get("https://api.example.com/data", payload={"data": {"value": 1}})
            import aiohttp

            async with aiohttp.ClientSession() as session:
                sem = asyncio.Semaphore(5)
                result = await fetch_source(session, simple_source, sem)

            assert result.elapsed_ms >= 0


class TestRetryableStatuses:
    def test_contains_429(self):
        assert 429 in RETRYABLE_STATUSES

    def test_contains_500(self):
        assert 500 in RETRYABLE_STATUSES

    def test_contains_502(self):
        assert 502 in RETRYABLE_STATUSES

    def test_contains_503(self):
        assert 503 in RETRYABLE_STATUSES

    def test_contains_504(self):
        assert 504 in RETRYABLE_STATUSES

    def test_200_not_retryable(self):
        assert 200 not in RETRYABLE_STATUSES


# ── fetch_all ────────────────────────────────────────────────────


class TestFetchAll:
    @pytest.mark.asyncio
    async def test_fetch_all_returns_list(self, sample_sources):
        with aioresponses() as mocked:
            mocked.get(
                "https://api.example.com/weather",
                payload={"current": {"temp": 15, "wind_speed": 4}},
            )
            mocked.get(
                "https://api.example.com/catfact",
                payload={"fact": "Cats are cool", "length": 13},
            )
            results = await fetch_all(sample_sources, timeout=10, max_concurrent=5, retries=1)

        assert isinstance(results, list)
        assert len(results) == 2

    @pytest.mark.asyncio
    async def test_fetch_all_preserves_order(self, sample_sources):
        with aioresponses() as mocked:
            mocked.get(
                "https://api.example.com/weather",
                payload={"current": {"temp": 10, "wind_speed": 2}},
            )
            mocked.get("https://api.example.com/catfact", payload={"fact": "Hi", "length": 2})
            results = await fetch_all(sample_sources, timeout=10, max_concurrent=5, retries=1)

        assert results[0].source_name == "weather"
        assert results[1].source_name == "catfact"

    @pytest.mark.asyncio
    async def test_fetch_all_partial_failure(self, sample_sources):
        with aioresponses() as mocked:
            mocked.get(
                "https://api.example.com/weather",
                payload={"current": {"temp": 10, "wind_speed": 2}},
            )
            mocked.get("https://api.example.com/catfact", status=500)
            mocked.get("https://api.example.com/catfact", status=500)
            results = await fetch_all(sample_sources, timeout=10, max_concurrent=5, retries=1)

        assert results[0].success is True
        assert results[1].success is False

    @pytest.mark.asyncio
    async def test_fetch_all_empty_sources(self):
        results = await fetch_all([], timeout=10, max_concurrent=5, retries=1)
        assert results == []

    @pytest.mark.asyncio
    async def test_fetch_all_results_are_fetch_result(self, sample_sources):
        with aioresponses() as mocked:
            mocked.get(
                "https://api.example.com/weather",
                payload={"current": {"temp": 10, "wind_speed": 2}},
            )
            mocked.get("https://api.example.com/catfact", payload={"fact": "X", "length": 1})
            results = await fetch_all(sample_sources, timeout=10, max_concurrent=5, retries=1)

        for r in results:
            assert isinstance(r, FetchResult)
