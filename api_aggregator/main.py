"""Точка входа: разбор CLI-аргументов и запуск.

Запуск:
    python -m api_aggregator.main [OPTIONS]
    python -m api_aggregator [OPTIONS]
"""

import argparse


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    """Разобрать аргументы командной строки.

    Аргументы:
        --config FILE          путь к конфигурации (default: config.json)
        --timeout SECONDS      таймаут запроса (default: 10)
        --max-concurrent N     макс. одновременных запросов (default: 5)
        --retries N            кол-во повторных попыток (default: 3)
        --output FILE          путь для сохранения отчёта
        --json                 формат отчёта — JSON
        --serve                запустить FastAPI-сервер
        --port PORT            порт сервера (default: 8000)

    Args:
        args: список аргументов (None = sys.argv[1:])

    Returns:
        argparse.Namespace с полями:
            config, timeout, max_concurrent, retries, output, json, serve, port
    """
    raise NotImplementedError("TODO: Реализуйте parse_args")


def main() -> None:
    """Главная функция.

    Алгоритм:
    1. Разобрать аргументы
    2. Загрузить конфигурацию
    3. Если --serve: создать и запустить FastAPI-сервер
    4. Иначе:
       a. Выполнить запросы (asyncio.run(fetch_all(...)))
       b. Агрегировать результаты
       c. Сформировать отчёт (текст или JSON)
       d. Вывести в stdout и/или сохранить в файл
    5. Обработать все ошибки без crash
    """
    raise NotImplementedError("TODO: Реализуйте main")


if __name__ == "__main__":
    main()
