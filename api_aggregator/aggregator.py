"""Агрегация результатов запросов."""

from datetime import datetime

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
    total_sources = len(results)
    successful = failed = total_time_ms = 0
    
    for result in results:
        if result.success: 
            successful += 1 
        else: 
            failed += 1

        total_time_ms += result.elapsed_ms

    return AggregatedReport(timestamp=datetime.now(), 
                            total_sources=total_sources, 
                            successful=successful, 
                            failed=failed, 
                            total_time_ms=total_time_ms, 
                            results=results)
