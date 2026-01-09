import os
from pathlib import Path
from typing import Any, Generic, Type, get_args, get_type_hints

import tomllib

from .exceptions import ConfigPropertyRequiredException, InvalidConfigException
from .types import BaseConfig, ConfigField, ConfigType


class ConfigHandler(Generic[ConfigType]):
    """
    Generic configuration handler that loads from TOML with environment variable overrides

    This class provides a lightweight, type-safe configuration handler based around dataclasses and type annotations to
    define configuration schemas

    Example:
        ```python
        from pathlib import Path
        from typing import List

        from pymicroconf.config_handler import ConfigHandler
        from pymicroconf.types import ConfigField, ConfigType

        class MyConfig(BaseConfig):
            api_key: Annotated[str, ConfigField("API_KEY", default="default_value")]
            debug: Annotated[bool, ConfigField("DEBUG", default=True)]

        config_handler = ConfigHandler(Path("config.toml"), MyConfig)
        config = config_handler.load_config()
        print(config.my_field)
        print(config.my_list)
        ```
    """

    _config_path: Path
    _config_class: Type[ConfigType]
    _config: ConfigType | None

    def __init__(self, config_file_path: Path, config_class: Type[ConfigType]):
        """
        Initialize the ConfigHandler with the given configuration file path and configuration class.

        Args:
            config_file_path (Path): The path to the configuration file.
            config_class (Type[ConfigType]): The top-level configuration class to use.
        """
        self._config_path = config_file_path
        self._config_class = config_class
        self._config = None

    def load_config(self) -> ConfigType:
        """
        Load the configuration from the file and return the parsed configuration object.

        Returns:
            ConfigType: The parsed configuration object.
        """

        raw_toml_config: dict[str, Any] = {}

        if self._config_path.exists():
            try:
                with open(self._config_path, "rb") as f:
                    raw_toml_config = tomllib.load(f)
            except Exception as e:
                print(
                    f"Error loading config file, continuing with just environment variables: (error: {e})"
                )
        else:
            print(f"{self._config_path} file not found, loading from environment only")
            raw_toml_config = {}

        self._config = self._parse_config(self._config_class, raw_toml_config)
        return self._config

    def _parse_config(
        self, container_class_type: Type[ConfigType], data: dict[str, Any]
    ) -> ConfigType:
        """
        Parse the raw data into a BaseConfig-extended object.

        Args:
            container_class_type (Type[ConfigType]): The top-level configuration class to use.
            data (dict[str, Any]): The configuration data to parse.

        Returns:
            ConfigType: The parsed configuration object.
        """
        if not issubclass(container_class_type, BaseConfig):
            raise TypeError(
                f"Config class {container_class_type} must be a subclass of BaseConfig"
            )

        kwargs: dict[str, Any] = {}
        hints = get_type_hints(container_class_type, include_extras=True)
        missing_fields: list[str] = []

        for field_name, field_hint in hints.items():
            sub_config_type, config_field = self._get_field_meta(field_hint=field_hint)
            try:
                if config_field:
                    kwargs[field_name] = self._parse_field_value(
                        field_type=sub_config_type,
                        field_name=field_name,
                        config_field=config_field,
                        toml_value=data.get(field_name),
                    )
                elif sub_config_type and issubclass(sub_config_type, BaseConfig):
                    kwargs[field_name] = self._parse_config(
                        sub_config_type, data.get(field_name, {})
                    )
                else:
                    kwargs[field_name] = data.get(field_name)
            except InvalidConfigException as e:
                missing_fields.extend(e.missing_fields)
            except ConfigPropertyRequiredException as e:
                missing_fields.append(e.field_name)
            except TypeError:
                # sub_config_type isn't a class so we just use the raw data
                kwargs[field_name] = data.get(field_name)
            except Exception as e:
                print(f"Error parsing field {field_name}, using raw value: {e}")
                kwargs[field_name] = data.get(field_name)

        if missing_fields:
            raise InvalidConfigException(missing_fields)

        return container_class_type(**kwargs)

    def _get_field_meta(
        self, field_hint: Any
    ) -> tuple[type, ConfigField] | tuple[type, None]:
        """
        Get the type and metadata for a field.

        Args:
            field_hint (Any): The type hint for the field.

        Returns:
            tuple[type, ConfigField] | tuple[type, None]: The type and metadata for the field.
        """
        args = get_args(field_hint)
        if len(args) == 0:
            return field_hint, None
        elif len(args) == 1:
            return args[0], None
        elif len(args) >= 2 and isinstance(args[1], ConfigField):
            return args[0], args[1]

        return args[0], None

    def _parse_field_value(
        self,
        field_type: type | None,
        field_name: str,
        config_field: ConfigField,
        toml_value: Any,
    ) -> Any:
        """
        Parse and verify the value of a field.

        Args:
            field_type (type | None): The type of the field.
            field_name (str): The name of the field.
            config_field (ConfigField): The metadata for the field.
            toml_value (Any): The value from the TOML file.

        Returns:
            Any: The parsed value.
        """
        config_val = toml_value

        if config_field.env_name in os.environ:
            # env vars always take precedence over config file values
            config_val = os.getenv(config_field.env_name)

        if config_val is None:
            if config_field.default is not None:
                return config_field.default
            elif config_field.required:
                raise ConfigPropertyRequiredException(field_name)

        return self._convert_value(config_val, field_type) if field_type else config_val

    def _convert_value(self, value: Any, target_type: type) -> Any:
        """
        Convert the value to the target type.

        Args:
            value (Any): The value to convert.
            target_type (type): The target type.

        Returns:
            Any: The converted value.
        """
        if isinstance(value, target_type):
            return value

        if isinstance(value, str):
            try:
                if target_type is bool:
                    return value.lower() in ("true", "1", "yes", "y", "on")
                elif target_type in (int, float):
                    return target_type(value)
                else:
                    return value
            except ValueError:
                raise ValueError(f"Invalid value for type {target_type}: {value}")

        return value

    @property
    def config(self) -> ConfigType:
        """
        Returns the actual config object.

        Returns:
            ConfigType: The configuration object.
        """
        if not self._config:
            self._config = self.load_config()

        return self._config
