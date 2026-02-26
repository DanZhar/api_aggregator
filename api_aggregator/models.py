"""Pydantic-модели данных.

Все структуры данных приложения описываются здесь.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class SourceConfig(BaseModel):
    """Конфигурация одного API-источника.

    Поля:
        name: уникальное имя источника
        url: URL эндпоинта
        params: query-параметры запроса
        method: HTTP-метод (GET по умолчанию)
        headers: дополнительные заголовки
        response_mapping: маппинг ключ_отчёта → путь в JSON-ответе (dot notation)
    """

    name: str
    url: str
    params: dict = Field(default_factory=dict)
    method: str = "GET"
    headers: dict[str, str] = Field(default_factory=dict)
    response_mapping: dict[str, str]


class AppConfig(BaseModel):
    """Полная конфигурация приложения.

    Поля:
        sources: список источников данных
    """

    sources: list[SourceConfig]


class FetchResult(BaseModel):
    """Результат запроса к одному API-источнику.

    Поля:
        source_name: имя источника
        success: успешность запроса
        data: извлечённые данные (после mapping) или None
        status_code: HTTP-статус ответа или None
        elapsed_ms: время запроса в миллисекундах
        error: описание ошибки или None
        retries_used: количество использованных повторных попыток
    """

    source_name: str
    success: bool
    data: dict | None = None
    status_code: int | None = None
    elapsed_ms: float = 0.0
    error: str | None = None
    retries_used: int = 0


class AggregatedReport(BaseModel):
    """Агрегированный отчёт по всем источникам.

    Поля:
        timestamp: время агрегации
        total_sources: общее количество источников
        successful: кол-во успешных
        failed: кол-во неуспешных
        total_time_ms: суммарное время всех запросов
        results: список FetchResult по каждому источнику
    """

    timestamp: datetime
    total_sources: int
    successful: int
    failed: int
    total_time_ms: float
    results: list[FetchResult]
