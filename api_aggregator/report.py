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
    generated_report = ["=== API Aggregator Report ==="]
    generated_report.append(f"Timestamp: {report.timestamp.isoformat(timespec='seconds')}")
    generated_report.append(
        f"Sources: {report.total_sources} total, {report.successful} successful, {report.failed} failed"
    )
    generated_report.append(f"Total time: {report.total_time_ms:.1f} ms")

    for result in report.results:
        if result.success:
            generated_report.append(
                f"\n--- {result.source_name} (OK, {result.elapsed_ms:.0f} ms) ---"
            )
            for k, v in result.data.items():
                generated_report.append(f"  {k}: {v}")
        else:
            generated_report.append(
                f"\n--- {result.source_name} (FAILED, {result.elapsed_ms:.0f} ms, retries: {result.retries_used}) ---"
            )
            generated_report.append(f"  error: {result.error}")

    return "\n".join(generated_report)


def generate_json_report(report: AggregatedReport) -> str:
    """Сформировать JSON-отчёт.

    Должен вернуть JSON-строку из report.model_dump(),
    с сериализацией datetime в ISO 8601, indent=2.

    Args:
        report: агрегированный отчёт

    Returns:
        str — JSON-строка
    """
    return report.model_dump_json(indent=2)


def save_report(content: str, filepath: str) -> None:
    """Сохранить отчёт в файл.

    Args:
        content: содержимое отчёта
        filepath: путь к файлу
    """
    with open(file=filepath, mode="w", encoding="utf-8") as file:
        file.write(content)
