"""Асинхронные запросы к API-источникам.

Все запросы выполняются через aiohttp с поддержкой:
- семафора для ограничения конкурентности
- таймаутов
- retry с экспоненциальным backoff
"""

import asyncio

import aiohttp

from api_aggregator.models import FetchResult, SourceConfig

RETRYABLE_STATUSES = {429, 500, 502, 503, 504}


async def fetch_source(
    session: aiohttp.ClientSession,
    source: SourceConfig,
    semaphore: asyncio.Semaphore,
    timeout: int = 10,
    retries: int = 3,
) -> FetchResult:
    """Выполнить запрос к одному API-источнику.

    Алгоритм:
    1. Захватить семафор
    2. Выполнить HTTP-запрос (method, url, params, headers)
    3. При ошибке (retryable status, timeout, connection error):
       - подождать 2^attempt секунд
       - повторить (до retries раз)
    4. При успехе: распарсить JSON, применить response_mapping
    5. Вернуть FetchResult

    Retryable-статусы: 429, 500, 502, 503, 504
    Retryable-ошибки: asyncio.TimeoutError, aiohttp.ClientError

    Args:
        session: aiohttp-сессия
        source: конфигурация источника
        semaphore: семафор для ограничения конкурентности
        timeout: таймаут в секундах
        retries: макс. кол-во повторных попыток

    Returns:
        FetchResult с результатом или ошибкой
    """
    raise NotImplementedError("TODO: Реализуйте fetch_source")


async def fetch_all(
    sources: list[SourceConfig],
    timeout: int = 10,
    max_concurrent: int = 5,
    retries: int = 3,
) -> list[FetchResult]:
    """Выполнить запросы ко всем источникам параллельно.

    Требования:
    - Создать aiohttp.ClientSession
    - Создать asyncio.Semaphore(max_concurrent)
    - Запустить все запросы через asyncio.gather
    - Вернуть список FetchResult в том же порядке, что и sources

    Args:
        sources: список конфигураций источников
        timeout: таймаут на один запрос
        max_concurrent: макс. одновременных запросов
        retries: кол-во повторных попыток

    Returns:
        Список FetchResult
    """
    raise NotImplementedError("TODO: Реализуйте fetch_all")
