"""
User configuration — persisted as JSON in the user's home directory.
"""
from __future__ import annotations

import json
import os
from typing import Any

CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".pdf_editor")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

DEFAULTS: dict[str, Any] = {
    "theme": "dark",
    "zoom_default": 1.0,
    "zoom_step": 0.1,
    "recent_files": [],
    "max_recent": 10,
    "sidebar_width": 180,
    "show_sidebar": True,
    "language": "fr",
    "tesseract_path": "",
}


class Config:
    def __init__(self) -> None:
        self._data: dict[str, Any] = dict(DEFAULTS)
        self._load()

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default if default is not None else DEFAULTS.get(key))

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value
        self._save()

    def add_recent_file(self, path: str) -> None:
        recent: list[str] = self._data.get("recent_files", [])
        if path in recent:
            recent.remove(path)
        recent.insert(0, path)
        self._data["recent_files"] = recent[: self._data.get("max_recent", 10)]
        self._save()

    def _load(self) -> None:
        if os.path.isfile(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    stored = json.load(f)
                self._data.update(stored)
            except Exception:
                pass

    def _save(self) -> None:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)
