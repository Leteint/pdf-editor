"""
Persistent library of custom image stamps.
Stamps are stored in ~/.pdf_editor/stamps/ as image files.
Metadata (name, default options) lives in stamps.json in the same folder.
"""
from __future__ import annotations

import json
import os
import shutil


class StampStore:
    """Manages the on-disk stamp library."""

    def __init__(self) -> None:
        from utils.config import CONFIG_DIR
        self._dir = os.path.join(CONFIG_DIR, "stamps")
        os.makedirs(self._dir, exist_ok=True)
        self._meta_path = os.path.join(self._dir, "stamps.json")
        self._stamps: list[dict] = self._load()

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _load(self) -> list[dict]:
        if os.path.exists(self._meta_path):
            try:
                with open(self._meta_path, encoding="utf-8") as f:
                    data = json.load(f)
                # Keep only entries whose image file still exists
                return [e for e in data
                        if os.path.exists(os.path.join(self._dir, e["file"]))]
            except Exception:
                pass
        return []

    def _save(self) -> None:
        with open(self._meta_path, "w", encoding="utf-8") as f:
            json.dump(self._stamps, f, ensure_ascii=False, indent=2)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def stamps(self) -> list[dict]:
        return list(self._stamps)

    def full_path(self, entry: dict) -> str:
        return os.path.join(self._dir, entry["file"])

    def add(self, image_path: str, name: str,
            position: str = "bottom-right",
            scale_pct: int = 25,
            opacity: float = 1.0) -> dict:
        """Copy *image_path* into the stamps folder and register it."""
        src_name = os.path.basename(image_path)
        dest     = os.path.join(self._dir, src_name)
        # Avoid filename collisions
        counter = 1
        base, ext = os.path.splitext(src_name)
        while os.path.exists(dest):
            dest = os.path.join(self._dir, f"{base}_{counter}{ext}")
            counter += 1
        shutil.copy2(image_path, dest)
        entry = {
            "file":      os.path.basename(dest),
            "name":      name,
            "position":  position,
            "scale_pct": scale_pct,
            "opacity":   opacity,
        }
        self._stamps.append(entry)
        self._save()
        return entry

    def remove(self, index: int) -> None:
        if 0 <= index < len(self._stamps):
            entry = self._stamps.pop(index)
            try:
                os.unlink(os.path.join(self._dir, entry["file"]))
            except FileNotFoundError:
                pass
            self._save()

    def update(self, index: int, **kwargs) -> None:
        if 0 <= index < len(self._stamps):
            self._stamps[index].update(kwargs)
            self._save()
