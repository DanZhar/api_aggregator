"""Формирование текстового и JSON-отчётов."""

from api_aggregator.models import AggregatedReport


def generate_text_report(report: AggregatedReport) -> str:
    """Сформировать текстовый отчёт.

    Формат:
        === API Aggregator Report ===
        Timestamp: 2025-01-15T14:30:00
        Sources: 3 total, 2 successful, 1 failed
        Total time: 1250.3 ms

        --- weather (OK, 320 ms) ---
          temperature: 15.2
          wind_speed: 4.5

        --- catfact (FAILED, 750 ms, retries: 3) ---
          error: Timeout after 10s

    Правила:
    - Источники в порядке из конфигурации
    - Успешные: статус OK + время
    - Неуспешные: FAILED + время + retries + error
    - Данные с отступом 2 пробела

    Args:
        report: агрегированный отчёт

    Returns:
        str — форматированный текстовый отчёт
    """
    raise NotImplementedError("TODO: Реализуйте generate_text_report")


def generate_json_report(report: AggregatedReport) -> str:
    """Сформировать JSON-отчёт.

    Должен вернуть JSON-строку из report.model_dump(),
    с сериализацией datetime в ISO 8601, indent=2.

    Args:
        report: агрегированный отчёт

    Returns:
        str — JSON-строка
    """
    raise NotImplementedError("TODO: Реализуйте generate_json_report")


def save_report(content: str, filepath: str) -> None:
    """Сохранить отчёт в файл.

    Args:
        content: содержимое отчёта
        filepath: путь к файлу
    """
    raise NotImplementedError("TODO: Реализуйте save_report")
