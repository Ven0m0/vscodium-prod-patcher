import re
from typing import Any

KEY_RE = re.compile(r"^%([A-Z]+)%$")


def alpm_ini_loads(data: str) -> dict[str, Any]:
    res: dict[str, Any] = {}
    key = None
    value: list[str] = []
    for line in data.splitlines():
        if key is None:
            m = KEY_RE.match(line)
            if m is None:
                continue
            key = m.group(1).lower()
            continue
        if not line:
            if len(value) == 1:
                res[key] = value.pop()
            else:
                res[key] = value
                value = []
            key = None
            continue
        value.append(line)
    return res
