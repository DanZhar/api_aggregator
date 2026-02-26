"""Тесты FastAPI-сервера."""

import pytest
from httpx import ASGITransport, AsyncClient

from api_aggregator.server import create_app


@pytest.fixture
def app(config_file):
    """Создать FastAPI-приложение для тестирования."""
    return create_app(
        config_path=config_file,
        timeout=5,
        max_concurrent=2,
        retries=1,
    )


class TestServerRoot:
    @pytest.mark.asyncio
    async def test_root_returns_200(self, app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_root_has_name(self, app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/")
        data = response.json()
        assert "name" in data


class TestServerReport:
    @pytest.mark.asyncio
    async def test_report_returns_200(self, app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/report")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_report_has_results(self, app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/report")
        data = response.json()
        assert "results" in data
        assert "total_sources" in data


class TestServerReportByName:
    @pytest.mark.asyncio
    async def test_existing_source(self, app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/report/weather")
        assert response.status_code == 200
        data = response.json()
        assert data["source_name"] == "weather"

    @pytest.mark.asyncio
    async def test_nonexistent_source_404(self, app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/report/nonexistent")
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()


class TestServerRefresh:
    @pytest.mark.asyncio
    async def test_refresh_returns_200(self, app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/refresh")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_refresh_returns_report(self, app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/refresh")
        data = response.json()
        assert "results" in data
        assert "total_sources" in data
