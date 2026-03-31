"""
Shared fixtures for all test modules.
"""
from __future__ import annotations

import os
import sys

import pikepdf
import pytest

# Ensure project root is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ---------------------------------------------------------------------------
# PDF fixtures
# ---------------------------------------------------------------------------

def _make_minimal_pdf(path: str, n_pages: int = 2) -> str:
    """Create a minimal valid PDF with *n_pages* blank pages at *path*."""
    pdf = pikepdf.Pdf.new()
    for _ in range(n_pages):
        page_obj = pdf.make_indirect(pikepdf.Dictionary(
            Type=pikepdf.Name.Page,
            MediaBox=pikepdf.Array([0, 0, 595, 842]),
            Resources=pikepdf.Dictionary(),
        ))
        pdf.pages.append(pikepdf.Page(page_obj))
    pdf.save(path)
    pdf.close()
    return path


@pytest.fixture()
def tmp_dir(tmp_path):
    """Alias for pytest's built-in tmp_path (returns pathlib.Path)."""
    return tmp_path


@pytest.fixture()
def minimal_pdf(tmp_path) -> str:
    """Path to a saved 2-page minimal PDF."""
    return _make_minimal_pdf(str(tmp_path / "test.pdf"), n_pages=2)


@pytest.fixture()
def minimal_pdf_4pages(tmp_path) -> str:
    """Path to a saved 4-page minimal PDF."""
    return _make_minimal_pdf(str(tmp_path / "test4.pdf"), n_pages=4)


@pytest.fixture()
def open_pdf(minimal_pdf) -> pikepdf.Pdf:
    """Already-opened pikepdf.Pdf (2 pages). Closed after the test."""
    pdf = pikepdf.open(minimal_pdf)
    yield pdf
    pdf.close()


# ---------------------------------------------------------------------------
# Image fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def rgb_png(tmp_path) -> str:
    """100×60 opaque red PNG."""
    from PIL import Image
    path = str(tmp_path / "rgb.png")
    Image.new("RGB", (100, 60), color=(200, 50, 50)).save(path)
    return path


@pytest.fixture()
def rgba_png(tmp_path) -> str:
    """100×60 semi-transparent green PNG (alpha channel)."""
    from PIL import Image
    path = str(tmp_path / "rgba.png")
    Image.new("RGBA", (100, 60), color=(50, 200, 50, 128)).save(path)
    return path


@pytest.fixture()
def jpeg_img(tmp_path) -> str:
    """100×60 JPEG image."""
    from PIL import Image
    path = str(tmp_path / "img.jpg")
    Image.new("RGB", (100, 60), color=(50, 50, 200)).save(path, format="JPEG")
    return path
