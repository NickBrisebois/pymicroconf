import os
from pathlib import Path

import pytest

from pymicroconf import ConfigHandler
from pymicroconf.exceptions import InvalidConfigException
from tests.unit.conftest import OptionalTestConfig, SimpleTestConfig


def test_load_config_from_file(tmp_config_file: Path):
    handler = ConfigHandler(tmp_config_file, SimpleTestConfig)
    config = handler.load_config()

    assert config is not None
    assert config.debug is True
    assert config.port == 9000
    assert config.timeout == 800.5


def test_load_config_with_defaults(empty_config_file: Path):
    override_val = "set using env"
    os.environ["API_KEY"] = override_val
    handler = ConfigHandler(empty_config_file, SimpleTestConfig)

    try:
        config = handler.load_config()
        assert config
        assert config.api_key == override_val

        assert config.debug is False
        assert config.port == 8080
        assert config.timeout == 5.0
    finally:
        os.environ.pop("API_KEY", None)


def test_load_config_variable_overrides(tmp_config_file: Path):
    api_key = "test api key"
    debug = "false"
    port = "7777"
    timeout = "5.0"

    os.environ["API_KEY"], os.environ["DEBUG"], os.environ["PORT"], os.environ["TIMEOUT"] = (
        api_key,
        debug,
        port,
        timeout,
    )
    handler = ConfigHandler(tmp_config_file, SimpleTestConfig)

    try:
        config = handler.load_config()
        assert config
        assert config.api_key == api_key
        assert config.debug is False
        assert config.port == int(port)
        assert config.timeout == 5.0

        # verify the type conversions explicitly
        assert isinstance(config.debug, bool)
        assert isinstance(config.port, int)
        assert isinstance(config.timeout, float)
    finally:
        os.environ.pop("API_KEY", None)
        os.environ.pop("DEBUG", None)
        os.environ.pop("PORT", None)


def test_missing_required_field_raises_exception(empty_config_file: Path):
    handler = ConfigHandler(empty_config_file, SimpleTestConfig)

    try:
        handler.load_config()
    except InvalidConfigException as e:
        assert e.missing_fields == ["api_key"]
    finally:
        os.environ.pop("API_KEY", None)


def test_optional_fields(empty_config_file: Path):
    handler = ConfigHandler(empty_config_file, OptionalTestConfig)
    config = handler.load_config()

    assert config.database_url is None
    assert config.cache_size == 100


@pytest.mark.parametrize(
    ("debug", "expected"),
    [
        ("true", True),
        ("false", False),
        ("1", True),
        ("0", False),
        ("yes", True),
        ("no", False),
        ("on", True),
        ("off", False),
    ],
)
def test_boolean_conversion_variations(debug: str, expected: bool, empty_config_file: Path):
    os.environ["API_KEY"] = "test_key"
    os.environ["DEBUG"] = debug

    try:
        handler = ConfigHandler(empty_config_file, SimpleTestConfig)
        config = handler.load_config()
        assert config.debug is expected, f"Expected {expected} for {debug} but got {config.debug}"
    finally:
        os.environ.pop("API_KEY", None)
        os.environ.pop("DEBUG", None)
