"""
Tests for PDFTools core operations: merge, split, reorder, compress.
"""
from __future__ import annotations

import os

import pikepdf
import pytest

from core.tools import PDFTools


# ---------------------------------------------------------------------------
# Merge
# ---------------------------------------------------------------------------

class TestMerge:
    def test_merge_two_pdfs(self, tmp_dir, minimal_pdf, minimal_pdf_4pages):
        out = str(tmp_dir / "merged.pdf")
        PDFTools.merge([minimal_pdf, minimal_pdf_4pages], out)
        with pikepdf.open(out) as pdf:
            assert len(pdf.pages) == 6  # 2 + 4

    def test_merge_single_pdf(self, tmp_dir, minimal_pdf):
        out = str(tmp_dir / "merged.pdf")
        PDFTools.merge([minimal_pdf], out)
        with pikepdf.open(out) as pdf:
            assert len(pdf.pages) == 2

    def test_merge_creates_file(self, tmp_dir, minimal_pdf):
        out = str(tmp_dir / "merged.pdf")
        assert not os.path.exists(out)
        PDFTools.merge([minimal_pdf], out)
        assert os.path.exists(out)


# ---------------------------------------------------------------------------
# Split
# ---------------------------------------------------------------------------

class TestSplitByChunk:
    def test_split_1_page_per_file(self, tmp_dir, minimal_pdf_4pages):
        paths = PDFTools.split_by_chunk(minimal_pdf_4pages, str(tmp_dir), pages_per_chunk=1)
        assert len(paths) == 4
        for p in paths:
            with pikepdf.open(p) as pdf:
                assert len(pdf.pages) == 1

    def test_split_2_pages_per_file(self, tmp_dir, minimal_pdf_4pages):
        paths = PDFTools.split_by_chunk(minimal_pdf_4pages, str(tmp_dir), pages_per_chunk=2)
        assert len(paths) == 2
        for p in paths:
            with pikepdf.open(p) as pdf:
                assert len(pdf.pages) == 2

    def test_split_chunk_larger_than_pdf(self, tmp_dir, minimal_pdf):
        paths = PDFTools.split_by_chunk(minimal_pdf, str(tmp_dir), pages_per_chunk=10)
        assert len(paths) == 1
        with pikepdf.open(paths[0]) as pdf:
            assert len(pdf.pages) == 2

    def test_split_output_files_exist(self, tmp_dir, minimal_pdf_4pages):
        paths = PDFTools.split_by_chunk(minimal_pdf_4pages, str(tmp_dir), pages_per_chunk=2)
        for p in paths:
            assert os.path.exists(p)


# ---------------------------------------------------------------------------
# Reorder pages
# ---------------------------------------------------------------------------

class TestReorderPages:
    def test_reverse_two_pages(self, open_pdf):
        """Reversing 2 pages should give page order [1, 0]."""
        page_specs = [(None, 1, 0), (None, 0, 0)]
        PDFTools.reorder_pages(open_pdf, page_specs)
        assert len(open_pdf.pages) == 2

    def test_page_count_preserved(self, open_pdf, minimal_pdf_4pages):
        extra = pikepdf.open(minimal_pdf_4pages)
        page_specs = [
            (None, 0, 0),
            (minimal_pdf_4pages, 0, 0),
            (minimal_pdf_4pages, 1, 0),
        ]
        extra.close()
        PDFTools.reorder_pages(open_pdf, page_specs)
        assert len(open_pdf.pages) == 3

    def test_rotation_applied(self, open_pdf):
        page_specs = [(None, 0, 90), (None, 1, 0)]
        PDFTools.reorder_pages(open_pdf, page_specs)
        rotate_val = int(open_pdf.pages[0].get("/Rotate", 0))
        assert rotate_val == 90

    def test_empty_specs_gives_empty_pdf(self, open_pdf):
        PDFTools.reorder_pages(open_pdf, [])
        assert len(open_pdf.pages) == 0


# ---------------------------------------------------------------------------
# Compress
# ---------------------------------------------------------------------------

class TestCompress:
    def test_compress_returns_int(self, open_pdf):
        result = PDFTools.compress(open_pdf)
        assert isinstance(result, int)

    def test_compress_pdf_remains_valid(self, tmp_dir, minimal_pdf):
        with pikepdf.open(minimal_pdf) as pdf:
            PDFTools.compress(pdf)
            out = str(tmp_dir / "compressed.pdf")
            pdf.save(out)
        with pikepdf.open(out) as pdf:
            assert len(pdf.pages) == 2
