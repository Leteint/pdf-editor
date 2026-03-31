"""
Tests for StampStore (utils/stamp_store.py).
"""
from __future__ import annotations

import os
import json
import pytest


@pytest.fixture()
def store(tmp_path, monkeypatch):
    """Isolated StampStore writing to a temp directory."""
    import utils.config as cfg_module
    monkeypatch.setattr(cfg_module, "CONFIG_DIR", str(tmp_path))
    from utils.stamp_store import StampStore
    return StampStore()


class TestStampStoreAdd:
    def test_add_returns_entry(self, store, rgb_png):
        entry = store.add(rgb_png, "Mon Tampon")
        assert entry["name"] == "Mon Tampon"
        assert "file" in entry

    def test_add_copies_file(self, store, rgb_png):
        entry = store.add(rgb_png, "Copie")
        assert os.path.exists(store.full_path(entry))

    def test_add_increments_stamps_list(self, store, rgb_png, rgba_png):
        assert len(store.stamps) == 0
        store.add(rgb_png,  "Tampon 1")
        store.add(rgba_png, "Tampon 2")
        assert len(store.stamps) == 2

    def test_add_handles_name_collision(self, store, rgb_png):
        """Adding the same filename twice must not overwrite the first copy."""
        e1 = store.add(rgb_png, "A")
        e2 = store.add(rgb_png, "B")
        assert e1["file"] != e2["file"]
        assert os.path.exists(store.full_path(e1))
        assert os.path.exists(store.full_path(e2))

    def test_add_default_options(self, store, rgb_png):
        entry = store.add(rgb_png, "T")
        assert entry["position"]  == "bottom-right"
        assert entry["scale_pct"] == 25
        assert entry["opacity"]   == 1.0

    def test_add_custom_options(self, store, rgb_png):
        entry = store.add(rgb_png, "T", position="top-left", scale_pct=50, opacity=0.7)
        assert entry["position"]  == "top-left"
        assert entry["scale_pct"] == 50
        assert entry["opacity"]   == pytest.approx(0.7)


class TestStampStoreRemove:
    def test_remove_deletes_file(self, store, rgb_png):
        entry = store.add(rgb_png, "À supprimer")
        path  = store.full_path(entry)
        store.remove(0)
        assert not os.path.exists(path)

    def test_remove_decrements_list(self, store, rgb_png, rgba_png):
        store.add(rgb_png,  "A")
        store.add(rgba_png, "B")
        store.remove(0)
        assert len(store.stamps) == 1

    def test_remove_out_of_range_is_noop(self, store, rgb_png):
        store.add(rgb_png, "X")
        store.remove(99)  # should not raise
        assert len(store.stamps) == 1


class TestStampStoreUpdate:
    def test_update_name(self, store, rgb_png):
        store.add(rgb_png, "Original")
        store.update(0, name="Modifié")
        assert store.stamps[0]["name"] == "Modifié"

    def test_update_opacity(self, store, rgb_png):
        store.add(rgb_png, "T")
        store.update(0, opacity=0.5)
        assert store.stamps[0]["opacity"] == pytest.approx(0.5)


class TestStampStorePersistence:
    def test_stamps_reload_across_instances(self, tmp_path, monkeypatch, rgb_png):
        import utils.config as cfg_module
        monkeypatch.setattr(cfg_module, "CONFIG_DIR", str(tmp_path))
        from utils.stamp_store import StampStore
        s1 = StampStore()
        s1.add(rgb_png, "Persistant")
        # New instance should reload from disk
        s2 = StampStore()
        assert len(s2.stamps) == 1
        assert s2.stamps[0]["name"] == "Persistant"

    def test_missing_image_file_filtered_on_load(self, tmp_path, monkeypatch, rgb_png):
        """Stamps whose image file is gone should be silently dropped on reload."""
        import utils.config as cfg_module
        monkeypatch.setattr(cfg_module, "CONFIG_DIR", str(tmp_path))
        from utils.stamp_store import StampStore
        s1 = StampStore()
        entry = s1.add(rgb_png, "Orphelin")
        # Manually delete the image file
        os.unlink(s1.full_path(entry))
        # Reload
        s2 = StampStore()
        assert len(s2.stamps) == 0
