"""Тесты загрузки конфигурации и extract_by_path."""

import json

import pytest

from api_aggregator.config import apply_response_mapping, extract_by_path, load_config
from api_aggregator.models import AppConfig

# ── load_config ──────────────────────────────────────────────────


class TestLoadConfig:
    def test_load_valid_config(self, config_file):
        config = load_config(config_file)
        assert isinstance(config, AppConfig)
        assert len(config.sources) == 2

    def test_source_names(self, config_file):
        config = load_config(config_file)
        names = [s.name for s in config.sources]
        assert "weather" in names
        assert "catfact" in names

    def test_file_not_found(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_config(str(tmp_path / "nonexistent.json"))

    def test_invalid_json(self, tmp_path):
        bad_file = tmp_path / "bad.json"
        bad_file.write_text("{invalid json")
        with pytest.raises((ValueError, Exception)):
            load_config(str(bad_file))

    def test_invalid_structure(self, tmp_path):
        bad_file = tmp_path / "bad.json"
        bad_file.write_text(json.dumps({"sources": [{"name": "x"}]}))
        with pytest.raises(Exception):
            load_config(str(bad_file))


# ── extract_by_path ──────────────────────────────────────────────


class TestExtractByPath:
    def test_simple_key(self):
        assert extract_by_path({"name": "Alice"}, "name") == "Alice"

    def test_nested_key(self):
        data = {"current_weather": {"temperature": 15.2}}
        assert extract_by_path(data, "current_weather.temperature") == 15.2

    def test_deeply_nested(self):
        data = {"a": {"b": {"c": {"d": 42}}}}
        assert extract_by_path(data, "a.b.c.d") == 42

    def test_dollar_returns_whole(self):
        data = {"key": "value"}
        assert extract_by_path(data, "$") == data

    def test_dollar_with_list(self):
        data = [1, 2, 3]
        assert extract_by_path(data, "$") == data

    def test_array_index(self):
        data = {"items": [10, 20, 30]}
        assert extract_by_path(data, "items.1") == 20

    def test_array_first_element(self):
        data = [{"name": "first"}, {"name": "second"}]
        assert extract_by_path(data, "0.name") == "first"

    def test_nonexistent_key_returns_none(self):
        assert extract_by_path({"a": 1}, "b") is None

    def test_nonexistent_nested_returns_none(self):
        assert extract_by_path({"a": {"b": 1}}, "a.c") is None

    def test_empty_dict(self):
        assert extract_by_path({}, "key") is None

    def test_index_out_of_range(self):
        assert extract_by_path([1, 2], "5") is None


# ── apply_response_mapping ──────────────────────────────────────


class TestApplyResponseMapping:
    def test_simple_mapping(self):
        raw = {"fact": "Cats are great", "length": 14}
        mapping = {"fact": "fact", "length": "length"}
        result = apply_response_mapping(raw, mapping)
        assert result["fact"] == "Cats are great"
        assert result["length"] == 14

    def test_nested_mapping(self):
        raw = {"current_weather": {"temperature": 15.2, "windspeed": 4.5}}
        mapping = {
            "temperature": "current_weather.temperature",
            "wind_speed": "current_weather.windspeed",
        }
        result = apply_response_mapping(raw, mapping)
        assert result["temperature"] == 15.2
        assert result["wind_speed"] == 4.5

    def test_dollar_mapping(self):
        raw = [{"name": "MIT"}, {"name": "Harvard"}]
        mapping = {"results": "$"}
        result = apply_response_mapping(raw, mapping)
        assert result["results"] == raw

    def test_missing_path_gives_none(self):
        raw = {"a": 1}
        mapping = {"missing": "b.c.d"}
        result = apply_response_mapping(raw, mapping)
        assert result["missing"] is None

    def test_returns_dict(self):
        result = apply_response_mapping({"a": 1}, {"key": "a"})
        assert isinstance(result, dict)
