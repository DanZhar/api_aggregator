"""FastAPI-сервер для отдачи агрегированных результатов.

Эндпоинты:
    GET  /              — информация о сервере
    GET  /report        — полный JSON-отчёт
    GET  /report/{name} — результат по конкретному источнику
    POST /refresh       — повторить запросы и обновить данные
"""

import asyncio

from fastapi import FastAPI, HTTPException

from api_aggregator.aggregator import aggregate
from api_aggregator.config import load_config
from api_aggregator.fetcher import fetch_all
from api_aggregator.models import AggregatedReport, FetchResult


def create_app(config_path: str, timeout: int, max_concurrent: int, retries: int) -> FastAPI:
    """Создать и настроить FastAPI-приложение.

    Требования:
    - Загрузить конфигурацию
    - Выполнить начальный сбор данных
    - Сохранить текущий report в app.state
    - Зарегистрировать эндпоинты

    GET /
        Возвращает: {"name": "API Aggregator", "version": "0.1.0", "sources": N}

    GET /report
        Возвращает: полный AggregatedReport как JSON

    GET /report/{name}
        Возвращает: FetchResult для указанного источника
        404 если источник не найден: {"detail": "Source '{name}' not found"}

    POST /refresh
        Повторно выполняет все запросы, обновляет report
        Возвращает: обновлённый AggregatedReport

    Args:
        config_path: путь к config.json
        timeout: таймаут запросов
        max_concurrent: макс. конкурентных запросов
        retries: кол-во повторных попыток

    Returns:
        Настроенный FastAPI app
    """
    print(type(timeout), type(max_concurrent), type(retries))
    app = FastAPI(title="API Aggregator", version="0.1.0")

    sources = load_config(filepath=config_path).sources
    results = asyncio.run(
        fetch_all(
            sources=sources,
            timeout=timeout,
            max_concurrent=max_concurrent,
            retries=retries,
        )
    )
    report = aggregate(results=results)

    app.state.report = report

    @app.get("/")
    def health() -> dict:
        return {"name": app.title, "version": app.version, "sources": len(sources)}

    @app.get("/report")
    def get_report() -> AggregatedReport:
        return app.state.report

    @app.get("/report/{name}")
    def get_report_by_name(name: str) -> FetchResult:
        for result in app.state.report.results:
            if result.source_name == name:
                return result

        raise HTTPException(status_code=404, detail=f"Source '{name}' not found")

    @app.post("/refresh")
    async def refresh() -> AggregatedReport:
        new_results = await fetch_all(
                    sources=sources,
                    timeout=timeout,
                    max_concurrent=max_concurrent,
                    retries=retries,
                )
        new_report = aggregate(results=new_results)
        app.state.report = new_report

        return new_report

    return app
