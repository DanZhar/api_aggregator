# Асинхронный агрегатор API

[![Run Tests](../../actions/workflows/run-tests.yml/badge.svg)](../../actions/workflows/run-tests.yml)

## Описание

Практический проект: консольное приложение + мини-сервер для параллельного опроса нескольких API, агрегации результатов и отдачи отчёта в текстовом/JSON-формате или через FastAPI.

Темы: **asyncio, aiohttp, FastAPI, Pydantic, retry, semaphore, dot-notation mapping**.

## Для учеников

### Быстрый старт

```bash
# 1. Форкните репозиторий, клонируйте
git clone https://github.com/<ваш-username>/api_aggregator.git
cd api_aggregator

# 2. Виртуальное окружение
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 3. Установка зависимостей
pip install -e ".[dev]"

# 4. Проверка
pytest -v
ruff check .
ruff format --check .

# 5. Push и PR
```

## Запуск

```bash
# Режим отчёта (по умолчанию)
python -m api_aggregator.main --config config.json

# С JSON-выводом
python -m api_aggregator.main --json --output report.json

# Режим сервера
python -m api_aggregator.main --serve --port 8000
```

### Параметры

| Параметр             | По умолчанию  | Описание                              |
| -------------------- | ------------- | ------------------------------------- |
| `--config FILE`      | `config.json` | Путь к файлу конфигурации             |
| `--timeout SECONDS`  | `10`          | Таймаут на один запрос                |
| `--max-concurrent N` | `5`           | Макс. одновременных запросов          |
| `--retries N`        | `3`           | Кол-во повторных попыток при ошибке   |
| `--output FILE`      | `None`        | Путь для сохранения отчёта            |
| `--json`             | `False`       | Формат отчёта — JSON                  |
| `--serve`            | `False`       | Запустить FastAPI-сервер              |
| `--port PORT`        | `8000`        | Порт для сервера                      |

### API-сервер (--serve)

| Метод | Путь              | Описание                              |
| ----- | ----------------- | ------------------------------------- |
| GET   | `/`               | Информация о сервере                  |
| GET   | `/report`         | Полный агрегированный отчёт (JSON)    |
| GET   | `/report/{name}`  | Результат по конкретному источнику    |
| POST  | `/refresh`        | Повторить запросы и обновить данные   |

## Структура проекта

```
api_aggregator/
├── pyproject.toml
├── README.md
├── config.json               # пример конфигурации
├── api_aggregator/
│   ├── __init__.py
│   ├── __main__.py
│   ├── main.py               # CLI, точка входа
│   ├── config.py             # загрузка/валидация конфигурации
│   ├── fetcher.py            # асинхронные запросы (aiohttp)
│   ├── aggregator.py         # агрегация результатов
│   ├── report.py             # текстовый и JSON-отчёты
│   ├── server.py             # FastAPI-эндпоинты
│   └── models.py             # Pydantic-модели
└── tests/
    ├── conftest.py
    ├── test_models.py
    ├── test_config.py
    ├── test_fetcher.py
    ├── test_aggregator.py
    ├── test_report.py
    ├── test_server.py
    └── test_cli.py
```

## CI/CD

На каждый PR автоматически:

1. **Lint & Format** — ruff
2. **Tests** — pytest на Python 3.10, 3.11, 3.12
3. **Structure Check** — наличие файлов + проверка импортов
