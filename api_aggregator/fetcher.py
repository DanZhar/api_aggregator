"""Асинхронные запросы к API-источникам.

Все запросы выполняются через aiohttp с поддержкой:
- семафора для ограничения конкурентности
- таймаутов
- retry с экспоненциальным backoff
"""

import asyncio

import aiohttp

import time

from api_aggregator.models import FetchResult, SourceConfig
from api_aggregator.config import apply_response_mapping


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

    last_error = None
    status_code = None

    start = time.monotonic() # запускаем таймер
    for attempt in range(retries + 1):
        try:
            async with semaphore:
                async with session.request(
                    method=source.method,
                    url=source.url,
                    params=source.params,
                    headers=source.headers,
                    timeout=aiohttp.ClientTimeout(total=timeout),
                ) as response:
                    status_code = response.status
                
                    if 200 <= status_code < 300:
                        raw_json = await response.json()
                        data = apply_response_mapping(raw_response=raw_json, mapping=source.response_mapping)
                        end = time.monotonic()
                        duration = (end - start) * 1000
                        return FetchResult(source_name=source.name, success=True, data=data, status_code=status_code, elapsed_ms=duration, error=last_error, retries_used=attempt)
                    elif status_code in (RETRYABLE_STATUSES):
                        last_error = f"HTTP {status_code}"
                    else:
                        end = time.monotonic()
                        duration = (end - start) * 1000
                        last_error = f"HTTP {status_code}"
                        return FetchResult(source_name=source.name, success=False, data=None, status_code=status_code, elapsed_ms=duration, error=last_error, retries_used=attempt)

            if attempt < retries:
                await asyncio.sleep(2**attempt)
                continue

        except (asyncio.TimeoutError, aiohttp.ClientError) as e:
            last_error = str(e)
            if attempt < retries:
                await asyncio.sleep(2**attempt)
                continue
        except (Exception) as e:
            end = time.monotonic()
            duration = (end - start) * 1000
            return FetchResult(source_name=source.name, success=False, data=None, status_code=status_code, elapsed_ms=duration, error=str(e), retries_used=attempt)

    end = time.monotonic()
    duration = (end - start) * 1000
    return FetchResult(source_name=source.name, success=False, data=None, status_code=status_code, elapsed_ms=duration, error=last_error ,retries_used=retries)


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

    async with aiohttp.ClientSession() as session:
        semaphore = asyncio.Semaphore(max_concurrent)

        tasks = [fetch_source(session=session, 
                              source=source, 
                              semaphore=semaphore, 
                              timeout=timeout, 
                              retries=retries) for source in sources]

        result = await asyncio.gather(*tasks)

    return result
