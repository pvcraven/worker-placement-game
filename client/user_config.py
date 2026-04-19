"""Persistent user configuration (player name, server address)."""

from __future__ import annotations

import json
from pathlib import Path

_CONFIG_DIR = Path.home() / ".record-label"
_CONFIG_FILE = _CONFIG_DIR / "config.json"

_DEFAULTS = {
    "name": "",
    "server": "ws://localhost:8765",
}


def load_config() -> dict:
    if _CONFIG_FILE.exists():
        try:
            data = json.loads(_CONFIG_FILE.read_text(encoding="utf-8"))
            return {**_DEFAULTS, **data}
        except (json.JSONDecodeError, OSError):
            pass
    return dict(_DEFAULTS)


def save_config(*, name: str, server: str) -> None:
    _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    _CONFIG_FILE.write_text(
        json.dumps({"name": name, "server": server}, indent=2),
        encoding="utf-8",
    )
