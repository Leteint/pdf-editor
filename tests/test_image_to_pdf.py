"""
Tests for the image → PDF conversion used by OrganizeDialog
and the Windows right-click context menu.
"""
from __future__ import annotations

import os
import pikepdf
import pytest

from ui.dialogs.organize_dialog import OrganizeDialog


class TestImageToPdf:
    """Tests for OrganizeDialog._image_to_temp_pdf (static helper)."""

    def test_rgb_png_produces_valid_pdf(self, tmp_path, rgb_png):
        out = OrganizeDialog._image_to_temp_pdf(rgb_png)
        try:
            assert os.path.exists(out)
            with pikepdf.open(out) as pdf:
                assert len(pdf.pages) == 1
        finally:
            os.unlink(out)

    def test_rgba_png_produces_valid_pdf(self, tmp_path, rgba_png):
        out = OrganizeDialog._image_to_temp_pdf(rgba_png)
        try:
            with pikepdf.open(out) as pdf:
                assert len(pdf.pages) == 1
        finally:
            os.unlink(out)

    def test_jpeg_produces_valid_pdf(self, tmp_path, jpeg_img):
        out = OrganizeDialog._image_to_temp_pdf(jpeg_img)
        try:
            with pikepdf.open(out) as pdf:
                assert len(pdf.pages) == 1
        finally:
            os.unlink(out)

    def test_multipage_tiff_produces_multiple_pages(self, tmp_path):
        """A 3-frame TIFF should yield a 3-page PDF."""
        from PIL import Image
        tiff_path = str(tmp_path / "multi.tiff")
        frames = [Image.new("RGB", (100, 60), color=(i * 60, 0, 0)) for i in range(3)]
        frames[0].save(tiff_path, save_all=True, append_images=frames[1:])

        out = OrganizeDialog._image_to_temp_pdf(tiff_path)
        try:
            with pikepdf.open(out) as pdf:
                assert len(pdf.pages) == 3
        finally:
            os.unlink(out)

    def test_output_is_temp_file_with_pdf_suffix(self, rgb_png):
        out = OrganizeDialog._image_to_temp_pdf(rgb_png)
        try:
            assert out.endswith(".pdf")
        finally:
            if os.path.exists(out):
                os.unlink(out)


class TestImageToPdfCliMode:
    """Tests for the --to-pdf entry point in main.py."""

    def test_converts_and_creates_pdf(self, tmp_path, rgb_png):
        """_run_image_to_pdf should create a .pdf next to the source image."""
        import shutil
        # Copy image to tmp_path so output goes there
        dest_img = str(tmp_path / "photo.png")
        shutil.copy(rgb_png, dest_img)
        expected_pdf = str(tmp_path / "photo.pdf")

        # Import the conversion function directly (without launching QApplication)
        import importlib, sys
        # Patch QApplication and QMessageBox to avoid GUI during tests
        from unittest.mock import MagicMock, patch
        with patch("PySide6.QtWidgets.QApplication"), \
             patch("PySide6.QtWidgets.QMessageBox"):
            import main as main_module
            main_module._run_image_to_pdf(dest_img)

        assert os.path.exists(expected_pdf)

    def test_nonexistent_file_does_not_crash(self, tmp_path):
        from unittest.mock import patch
        with patch("PySide6.QtWidgets.QApplication"), \
             patch("PySide6.QtWidgets.QMessageBox"):
            import main as main_module
            # Should not raise — shows error dialog instead
            main_module._run_image_to_pdf(str(tmp_path / "ghost.png"))

    def test_auto_increment_if_pdf_exists(self, tmp_path, rgb_png):
        import shutil
        dest_img = str(tmp_path / "doc.png")
        shutil.copy(rgb_png, dest_img)
        # Pre-create doc.pdf so auto-increment kicks in
        open(str(tmp_path / "doc.pdf"), "wb").close()

        from unittest.mock import patch
        with patch("PySide6.QtWidgets.QApplication"), \
             patch("PySide6.QtWidgets.QMessageBox"):
            import main as main_module
            main_module._run_image_to_pdf(dest_img)

        assert os.path.exists(str(tmp_path / "doc_1.pdf"))
