"""Агрегация результатов запросов."""

from api_aggregator.models import AggregatedReport, FetchResult


def aggregate(results: list[FetchResult]) -> AggregatedReport:
    """Собрать агрегированный отчёт из списка результатов.

    Вычисляет:
    - timestamp: текущее время
    - total_sources: len(results)
    - successful: количество результатов с success=True
    - failed: количество результатов с success=False
    - total_time_ms: сумма elapsed_ms всех результатов
    - results: исходный список

    Args:
        results: список FetchResult

    Returns:
        AggregatedReport
    """
    raise NotImplementedError("TODO: Реализуйте aggregate")
