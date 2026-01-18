import os
import tomllib
import tomli_w
from pathlib import Path
from typing import Any, Optional

from ..consts import ENCODING
from .paths import CONFIG_DIR, CONFIG_PATH
from .schema import Config

CONFIG: Optional[Config] = None

EXTENSION_SOURCES = ["openvsx", "microsoft"]


def toml_load(path: Path):
    # tomllib requires binary mode
    with open(path, "rb") as file:
        return tomllib.load(file)


def toml_save(path: Path, obj: Any):
    # tomli_w produces a string; write it as utf-8 text
    with open(path, "wt", encoding=ENCODING) as file:
        file.write(tomli_w.dumps(obj))


def load_config() -> Config:
    try:
        return Config.from_dict(toml_load(CONFIG_PATH))
    except FileNotFoundError:
        return Config()


def get_config(force_reload: bool = False) -> Config:
    # pylint: disable=global-statement
    global CONFIG
    if CONFIG is None or force_reload:
        CONFIG = load_config()
    return CONFIG


def save_config(config: Config):
    if not CONFIG_DIR.exists():
        os.makedirs(CONFIG_DIR)
    toml_save(CONFIG_PATH, config.to_dict())
