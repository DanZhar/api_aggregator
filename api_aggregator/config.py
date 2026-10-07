"""Загрузка и валидация конфигурации из JSON-файла."""

import json
import os
from json import JSONDecodeError

from api_aggregator.models import AppConfig


def load_config(filepath: str) -> AppConfig:
    """Загрузить и валидировать конфигурацию из JSON-файла.

    Требования:
    - Прочитать JSON-файл
    - Валидировать через Pydantic-модель AppConfig
    - При отсутствии файла — FileNotFoundError с понятным сообщением
    - При невалидном JSON — ValueError с описанием проблемы
    - При невалидной структуре — Pydantic ValidationError

    Args:
        filepath: путь к JSON-файлу

    Returns:
        AppConfig — валидированная конфигурация
    """

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File {filepath} does not exist.")

    try:
        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)
    except JSONDecodeError as e:
        raise ValueError(f"Failed to parse json: {filepath} : {e}") from e
    except OSError as e:
        raise ValueError(f"Failed to open JSON: {filepath}: {e}") from e

    return AppConfig(**data)


def extract_by_path(data: dict | list, path: str):
    """Извлечь значение из вложенной структуры по dot-notation пути.

    Примеры:
        extract_by_path({"a": {"b": 1}}, "a.b") → 1
        extract_by_path([{"name": "x"}], "0.name") → "x"
        extract_by_path({"items": [1, 2]}, "items.1") → 2
        extract_by_path(data, "$") → data  (весь объект целиком)

    Правила:
    - "$" — вернуть весь объект
    - Числовые сегменты — индекс в массиве
    - Строковые сегменты — ключ в словаре
    - При несуществующем пути — вернуть None

    Args:
        data: корневой объект (dict или list)
        path: путь в dot-notation

    Returns:
        Извлечённое значение или None
    """

    if path == "$":
        return data

    splitted_path = path.split(".")
    res = data

    for step in splitted_path:
        if step.isdigit():
            try:
                res = res[int(step)]
            except (IndexError, TypeError):
                res = None
                break
        else:
            try:
                res = res[step]
            except (KeyError, TypeError):
                res = None
                break

    return res


def apply_response_mapping(raw_response: dict | list, mapping: dict[str, str]) -> dict:
    """Применить response_mapping к сырому ответу API.

    Для каждого ключа в mapping извлечь значение из raw_response
    по указанному dot-notation пути.

    Args:
        raw_response: сырой JSON-ответ API
        mapping: словарь {ключ_отчёта: путь_в_ответе}

    Returns:
        dict с извлечёнными значениями
    """

    res = {}
    for report_key, path in mapping.items():
        res[report_key] = extract_by_path(data=raw_response, path=path)

    return res
