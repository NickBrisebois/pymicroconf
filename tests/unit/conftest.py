import tempfile
from collections.abc import Generator
from pathlib import Path
from typing import Annotated

import pytest

from pymicroconf import BaseConfig, ConfigField, ConfigHandler
from pymicroconf.exceptions import ConfigPropertyRequiredException, InvalidConfigException


class SimpleTestConfig(BaseConfig):
    api_key: Annotated[str, ConfigField("API_KEY", required=True)]
    debug: Annotated[bool, ConfigField("DEBUG", required=False, default=False)]
    port: Annotated[int, ConfigField("PORT", default=8080)]
    timeout: Annotated[float, ConfigField("TIMEOUT", default=5.0)]


class OptionalTestConfig(BaseConfig):
    database_url: Annotated[str, ConfigField("DATABASE_URL", required=False)]
    cache_size: Annotated[int, ConfigField("CACHE_SIZE", default=100)]


class NestedTestConfig(BaseConfig):
    name: Annotated[str, ConfigField("APP_NAME", required=True)]
    simple: SimpleTestConfig
    optional: OptionalTestConfig


@pytest.fixture
def tmp_config_file() -> Generator[Path, None, None]:
    tmp_path: Path | None = None

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write(
            """
            api_key = "test_api_key"
            debug = true
            port = 9000
            timeout = 800.5

            [simple]
            api_key = "nested_api_key"
            debug = false
            port = 8081

            [optional]
            database_url = "sqlite:///:memory:"
            cache_size = 200
            """
        )
        tmp_path = Path(f.name)

    yield tmp_path
    tmp_path.unlink()


@pytest.fixture
def empty_config_file() -> Generator[Path, None, None]:
    tmp_path: Path | None = None

    with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
        f.write("")
        tmp_path = Path(f.name)

    yield tmp_path
    tmp_path.unlink()


@pytest.fixture
def nonexistent_config_file() -> Path:
    return Path("/tmp/thisdoesntexist:).toml")
