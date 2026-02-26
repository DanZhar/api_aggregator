"""Тесты CLI (парсинг аргументов)."""

from api_aggregator.main import parse_args


class TestParseArgsDefaults:
    def test_default_config(self):
        args = parse_args([])
        assert args.config == "config.json"

    def test_default_timeout(self):
        args = parse_args([])
        assert args.timeout == 10

    def test_default_max_concurrent(self):
        args = parse_args([])
        assert args.max_concurrent == 5

    def test_default_retries(self):
        args = parse_args([])
        assert args.retries == 3

    def test_default_output_none(self):
        args = parse_args([])
        assert args.output is None

    def test_default_json_false(self):
        args = parse_args([])
        assert args.json is False

    def test_default_serve_false(self):
        args = parse_args([])
        assert args.serve is False

    def test_default_port(self):
        args = parse_args([])
        assert args.port == 8000


class TestParseArgsCustom:
    def test_config_flag(self):
        args = parse_args(["--config", "custom.json"])
        assert args.config == "custom.json"

    def test_timeout_flag(self):
        args = parse_args(["--timeout", "30"])
        assert args.timeout == 30

    def test_max_concurrent_flag(self):
        args = parse_args(["--max-concurrent", "10"])
        assert args.max_concurrent == 10

    def test_retries_flag(self):
        args = parse_args(["--retries", "5"])
        assert args.retries == 5

    def test_output_flag(self):
        args = parse_args(["--output", "report.txt"])
        assert args.output == "report.txt"

    def test_json_flag(self):
        args = parse_args(["--json"])
        assert args.json is True

    def test_serve_flag(self):
        args = parse_args(["--serve"])
        assert args.serve is True

    def test_port_flag(self):
        args = parse_args(["--port", "3000"])
        assert args.port == 3000


class TestParseArgsCombined:
    def test_all_flags(self):
        args = parse_args(
            [
                "--config",
                "my.json",
                "--timeout",
                "20",
                "--max-concurrent",
                "8",
                "--retries",
                "2",
                "--output",
                "out.json",
                "--json",
                "--serve",
                "--port",
                "9000",
            ]
        )
        assert args.config == "my.json"
        assert args.timeout == 20
        assert args.max_concurrent == 8
        assert args.retries == 2
        assert args.output == "out.json"
        assert args.json is True
        assert args.serve is True
        assert args.port == 9000


class TestParseArgsTypes:
    def test_timeout_is_int(self):
        args = parse_args(["--timeout", "5"])
        assert isinstance(args.timeout, int)

    def test_max_concurrent_is_int(self):
        args = parse_args(["--max-concurrent", "3"])
        assert isinstance(args.max_concurrent, int)

    def test_retries_is_int(self):
        args = parse_args(["--retries", "1"])
        assert isinstance(args.retries, int)

    def test_port_is_int(self):
        args = parse_args(["--port", "8080"])
        assert isinstance(args.port, int)
