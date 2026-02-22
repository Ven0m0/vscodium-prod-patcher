import json
import sys
from pathlib import Path
from typing import Any

from .consts import ENCODING


def eprint(*args: object, **kwargs):
    "Prints to stderr"
    print(*args, file=sys.stderr, **kwargs)


def err(*args: object, exit_code=1, **kwargs):
    eprint(*args, **kwargs)
    sys.exit(exit_code)


def text_file_write(path: Path, txt: str):
    try:
        with open(path, "wt", encoding=ENCODING) as file:
            file.write(txt)
    except OSError as e:
        err(f"Failed to write text to '{path}': {e}")


def json_load(path: Path):
    try:
        with open(path, "rt", encoding=ENCODING) as file:
            return json.load(file)
    except (ValueError, OSError) as e:
        err(f"Failed to read JSON from '{path}': {e}")


def json_write(path: Path, obj: Any, *args, **kwargs):
    try:
        with open(path, "wt", encoding=ENCODING) as file:
            json.dump(obj, file, *args, **kwargs)
    except (OSError, TypeError) as e:
        err(f"Failed to write JSON to '{path}': {e}")
