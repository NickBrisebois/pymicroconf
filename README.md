# PyMicroConf

A lightweight, type-safe TOML configuration loader with environment variable overrides for Python applications.

PyMicroConf provides a simple way to manage application configuration using TOML files while supporting environment variable overrides. It uses Python dataclasses and type annotations for type safety and automatic validation.

## Features

-  **Lightweight**: Minimal dependencies, uses only Python standard library
-  **Type-safe**: Full type checking with dataclasses and type annotations
-  **Environment Override**: Environment variables take precedence over config files
-  **Nested Configuration**: Support for nested configuration structures
- **Automatic Validation**: Built-in validation for required fields and types
-  **Easy to Use**: Intuitive API with minimal boilerplate

## Installation

```bash
pip install pymicroconf
```

## Usage

Define a configuration class using dataclasses and type annotations:

```python
from pathlib import Path
from typing import Annotated
from pymicroconf import ConfigHandler, ConfigField, BaseConfig

class AppConfig(BaseConfig):
    api_key: Annotated[str, ConfigField("API_KEY", required=True)]
    database_url: Annotated[str, ConfigField("DATABASE_URL", required=True)]
    debug: Annotated[str, ConfigField("DEBUG", default=False)]

config = Config(Path("config.toml"), AppConfig).load_config()
```

Access configuration values:

```python
print(config.api_key)
print(config.database_url)
print(config.debug)
```
