"""Точка входа: разбор CLI-аргументов и запуск.

Запуск:
    python -m api_aggregator.main [OPTIONS]
    python -m api_aggregator [OPTIONS]
"""

import argparse
import asyncio
import sys

import uvicorn

from api_aggregator.aggregator import aggregate
from api_aggregator.config import load_config
from api_aggregator.fetcher import fetch_all
from api_aggregator.report import generate_json_report, generate_text_report, save_report
from api_aggregator.server import create_app


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
    parser = argparse.ArgumentParser(
        prog="api_aggregator",
        description="Practical Project: A console application + a mini-server for simultaneously querying multiple APIs, aggregating the results, and generating reports in text or JSON format, or via FastAPI.",
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config.json",
        help="Path to config file (default: %(default)s)",
    )
    parser.add_argument(
        "--timeout", type=int, default=10, help="Request timeout in seconds (default: %(default)s)"
    )
    parser.add_argument(
        "--max-concurrent",
        type=int,
        default=5,
        help="Maximum number of concurrent requests (default: %(default)s)",
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=3,
        help="Maximum number of retries with backoff (default: %(default)s)",
    )
    parser.add_argument("--output", type=str, default=None, help="Path for saving the report")
    parser.add_argument("--json", action="store_true", help="Generate report in JSON format")
    parser.add_argument("--serve", action="store_true", help="Start the FastAPI server")
    parser.add_argument("--port", type=int, default=8000, help="Server port (default: %(default)s)")

    return parser.parse_args(args)


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
    args = parse_args()
    try:
        sources = load_config(args.config).sources
    except FileNotFoundError:
        print(f"config file not found: {args.config}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"invalid config '{args.config}': {e}", file=sys.stderr)
        sys.exit(1)

    try:
        if args.serve:
            app = create_app(
                config_path=args.config,
                timeout=args.timeout,
                max_concurrent=args.max_concurrent,
                retries=args.retries,
            )
            uvicorn.run(app=app, port=args.port)
        else:
            results = asyncio.run(
                fetch_all(
                    sources=sources,
                    timeout=args.timeout,
                    max_concurrent=args.max_concurrent,
                    retries=args.retries,
                )
            )
            report = aggregate(results=results)
            if args.json:
                generated_report = generate_json_report(report=report)
            else:
                generated_report = generate_text_report(report=report)

            if args.output:
                try:
                    save_report(content=generated_report, filepath=args.output)
                except OSError as e:
                    print(f"cannot save report to '{args.output}': {e}", file=sys.stderr)
                    sys.exit(1)

            print(generated_report)
    except KeyboardInterrupt:
        print("interrupted by user", file=sys.stderr)
        return sys.exit(130)
    except Exception as e:
        print(f"unexpected failure: {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
