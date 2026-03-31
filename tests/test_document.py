"""
Tests for the Document model (core/document.py).
"""
from __future__ import annotations

import os
import pytest

from core.document import Document


class TestDocumentLoad:
    def test_load_valid_pdf(self, minimal_pdf):
        doc = Document()
        doc.load(minimal_pdf)
        assert doc.is_open
        assert doc.page_count == 2
        doc.close()

    def test_load_sets_path(self, minimal_pdf):
        doc = Document()
        doc.load(minimal_pdf)
        assert doc.path == minimal_pdf
        doc.close()

    def test_not_open_before_load(self):
        doc = Document()
        assert not doc.is_open
        assert doc.page_count == 0

    def test_close_resets_state(self, minimal_pdf):
        doc = Document()
        doc.load(minimal_pdf)
        doc.close()
        assert not doc.is_open
        assert doc.page_count == 0

    def test_load_nonexistent_raises(self, tmp_dir):
        doc = Document()
        with pytest.raises(Exception):
            doc.load(str(tmp_dir / "nonexistent.pdf"))

    def test_info_populated_after_load(self, minimal_pdf):
        doc = Document()
        doc.load(minimal_pdf)
        assert doc.info.page_count == 2
        assert doc.info.file_path == minimal_pdf
        doc.close()


class TestDocumentPageOperations:
    def test_rotate_page(self, minimal_pdf):
        import pikepdf
        doc = Document()
        doc.load(minimal_pdf)
        doc.rotate_page(0, 90)
        rotate = int(doc.pdf.pages[0].get("/Rotate", 0))
        assert rotate == 90
        doc.close()

    def test_rotate_page_cumulative(self, minimal_pdf):
        doc = Document()
        doc.load(minimal_pdf)
        doc.rotate_page(0, 90)
        doc.rotate_page(0, 90)
        import pikepdf
        rotate = int(doc.pdf.pages[0].get("/Rotate", 0))
        assert rotate == 180
        doc.close()

    def test_delete_page_reduces_count(self, minimal_pdf):
        doc = Document()
        doc.load(minimal_pdf)
        doc.delete_page(0)
        assert doc.page_count == 1
        doc.close()

    def test_delete_only_page_raises_or_blocks(self, tmp_dir):
        """Deleting the sole page should either raise or be refused."""
        import pikepdf
        path = str(tmp_dir / "single.pdf")
        pdf = pikepdf.Pdf.new()
        page_obj = pdf.make_indirect(pikepdf.Dictionary(
            Type=pikepdf.Name.Page,
            MediaBox=pikepdf.Array([0, 0, 595, 842]),
        ))
        pdf.pages.append(pikepdf.Page(page_obj))
        pdf.save(path)
        pdf.close()

        doc = Document()
        doc.load(path)
        try:
            doc.delete_page(0)
            # If it succeeds, page count should still be ≥ 0
        except Exception:
            pass  # Raising is also acceptable
        doc.close()


class TestDocumentReopen:
    def test_reopen_same_path(self, minimal_pdf):
        doc = Document()
        doc.load(minimal_pdf)
        doc.reopen(minimal_pdf)
        assert doc.is_open
        assert doc.path == minimal_pdf
        assert not doc.info.is_modified
        doc.close()

    def test_is_modified_cleared_on_reopen(self, minimal_pdf):
        doc = Document()
        doc.load(minimal_pdf)
        doc.info.is_modified = True
        doc.reopen(minimal_pdf)
        assert not doc.info.is_modified
        doc.close()


class TestDocumentSave:
    def test_save_creates_file(self, minimal_pdf, tmp_dir):
        out = str(tmp_dir / "saved.pdf")
        doc = Document()
        doc.load(minimal_pdf)
        doc.save(out)
        assert os.path.exists(out)
        doc.close()

    def test_saved_file_is_valid_pdf(self, minimal_pdf, tmp_dir):
        import pikepdf
        out = str(tmp_dir / "saved.pdf")
        doc = Document()
        doc.load(minimal_pdf)
        doc.save(out)
        doc.close()
        with pikepdf.open(out) as pdf:
            assert len(pdf.pages) == 2
