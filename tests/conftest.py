"""Фикстуры для тестов."""

import json

import pytest

from api_aggregator.models import AppConfig, FetchResult, SourceConfig


@pytest.fixture
def weather_source():
    return SourceConfig(
        name="weather",
        url="https://api.example.com/weather",
        params={"lat": 55.75, "lon": 37.61},
        method="GET",
        headers={},
        response_mapping={
            "temperature": "current.temp",
            "wind": "current.wind_speed",
        },
    )


@pytest.fixture
def catfact_source():
    return SourceConfig(
        name="catfact",
        url="https://api.example.com/catfact",
        params={},
        method="GET",
        headers={},
        response_mapping={"fact": "fact", "length": "length"},
    )


@pytest.fixture
def sample_sources(weather_source, catfact_source):
    return [weather_source, catfact_source]


@pytest.fixture
def sample_config(sample_sources):
    return AppConfig(sources=sample_sources)


@pytest.fixture
def successful_result():
    return FetchResult(
        source_name="weather",
        success=True,
        data={"temperature": 15.2, "wind": 4.5},
        status_code=200,
        elapsed_ms=320.0,
        retries_used=0,
    )


@pytest.fixture
def failed_result():
    return FetchResult(
        source_name="catfact",
        success=False,
        data=None,
        status_code=None,
        elapsed_ms=750.0,
        error="Timeout after 10s",
        retries_used=3,
    )


@pytest.fixture
def sample_results(successful_result, failed_result):
    return [successful_result, failed_result]


@pytest.fixture
def config_file(tmp_path, sample_sources):
    """Создаёт временный config.json."""
    config_data = {"sources": [s.model_dump() for s in sample_sources]}
    filepath = tmp_path / "config.json"
    filepath.write_text(json.dumps(config_data))
    return str(filepath)
