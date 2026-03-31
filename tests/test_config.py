"""
Tests for Config (utils/config.py).
"""
from __future__ import annotations

import json
import os
import pytest


@pytest.fixture()
def config(tmp_path, monkeypatch):
    """Isolated Config instance writing to a temp directory."""
    import utils.config as cfg_module
    monkeypatch.setattr(cfg_module, "CONFIG_DIR",  str(tmp_path))
    monkeypatch.setattr(cfg_module, "CONFIG_FILE", str(tmp_path / "config.json"))
    from utils.config import Config
    return Config()


class TestConfigDefaults:
    def test_default_language(self, config):
        assert config.get("language") == "fr"

    def test_default_theme(self, config):
        assert config.get("theme") == "dark"

    def test_default_recent_files_empty(self, config):
        assert config.get("recent_files") == []

    def test_unknown_key_returns_none(self, config):
        assert config.get("non_existent_key") is None

    def test_unknown_key_with_default(self, config):
        assert config.get("non_existent_key", "fallback") == "fallback"


class TestConfigSetGet:
    def test_set_and_get_string(self, config):
        config.set("language", "en")
        assert config.get("language") == "en"

    def test_set_and_get_int(self, config):
        config.set("sidebar_width", 250)
        assert config.get("sidebar_width") == 250

    def test_set_and_get_bool(self, config):
        config.set("show_sidebar", False)
        assert config.get("show_sidebar") is False

    def test_set_persists_to_disk(self, tmp_path, monkeypatch):
        import utils.config as cfg_module
        monkeypatch.setattr(cfg_module, "CONFIG_DIR",  str(tmp_path))
        monkeypatch.setattr(cfg_module, "CONFIG_FILE", str(tmp_path / "config.json"))
        from utils.config import Config
        c1 = Config()
        c1.set("language", "es")
        # New instance reads from disk
        c2 = Config()
        assert c2.get("language") == "es"


class TestConfigRecentFiles:
    def test_add_recent_file(self, config):
        config.add_recent_file("/path/to/file.pdf")
        assert "/path/to/file.pdf" in config.get("recent_files")

    def test_recent_file_moved_to_front(self, config):
        config.add_recent_file("/a.pdf")
        config.add_recent_file("/b.pdf")
        config.add_recent_file("/a.pdf")
        recent = config.get("recent_files")
        assert recent[0] == "/a.pdf"

    def test_no_duplicate_in_recent(self, config):
        config.add_recent_file("/a.pdf")
        config.add_recent_file("/a.pdf")
        recent = config.get("recent_files")
        assert recent.count("/a.pdf") == 1

    def test_recent_files_limited_to_max(self, config):
        max_r = config.get("max_recent", 10)
        for i in range(max_r + 5):
            config.add_recent_file(f"/file_{i}.pdf")
        assert len(config.get("recent_files")) <= max_r
