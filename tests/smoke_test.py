"""
Verify that the package can be installed and imported.
"""


def test_import():
    from pathlib import Path

    from pymicroconf import BaseConfig, ConfigHandler

    ConfigHandler(config_file_path=Path("tests/test_config.yaml"), config_class=BaseConfig)


def test_version():
    from pymicroconf import __version__

    assert __version__ == "0.9.24"


try:
    test_import()
    test_version()
except Exception as e:
    print(f"Test failed: {e}")
    raise RuntimeError("Could not import package")
