"""FastAPI-сервер для отдачи агрегированных результатов.

Эндпоинты:
    GET  /              — информация о сервере
    GET  /report        — полный JSON-отчёт
    GET  /report/{name} — результат по конкретному источнику
    POST /refresh       — повторить запросы и обновить данные
"""

from fastapi import FastAPI

from api_aggregator.config import load_config


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

    app = FastAPI(title="API Aggregator", version="0.1.0")

    sources = load_config(filepath=config_path).sources

    @app.get("/")
    def health() -> dict:
        return {"name": app.title, "version": app.version, "sources": len(sources)}

    return app
