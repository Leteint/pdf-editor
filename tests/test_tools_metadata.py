"""
Tests for PDFTools metadata operations: get_metadata, set_metadata.
"""
from __future__ import annotations

import pikepdf
import pytest

from core.tools import PDFTools


class TestGetMetadata:
    def test_empty_pdf_returns_empty_strings(self, open_pdf):
        meta = PDFTools.get_metadata(open_pdf)
        assert isinstance(meta, dict)
        for key in ("title", "author", "subject", "keywords", "creator"):
            assert key in meta
            assert isinstance(meta[key], str)

    def test_returns_all_keys(self, open_pdf):
        meta = PDFTools.get_metadata(open_pdf)
        expected_keys = {"title", "author", "subject", "keywords", "creator"}
        assert expected_keys.issubset(meta.keys())


class TestSetMetadata:
    def test_set_and_get_title(self, open_pdf):
        PDFTools.set_metadata(open_pdf, {"title": "Mon Document"})
        meta = PDFTools.get_metadata(open_pdf)
        assert meta["title"] == "Mon Document"

    def test_set_and_get_author(self, open_pdf):
        PDFTools.set_metadata(open_pdf, {"author": "Jean Dupont"})
        meta = PDFTools.get_metadata(open_pdf)
        assert meta["author"] == "Jean Dupont"

    def test_set_all_fields(self, open_pdf):
        data = {
            "title":    "Titre Test",
            "author":   "Auteur Test",
            "subject":  "Sujet Test",
            "keywords": "mot1, mot2",
            "creator":  "PDF Editor",
        }
        PDFTools.set_metadata(open_pdf, data)
        meta = PDFTools.get_metadata(open_pdf)
        for key, val in data.items():
            assert meta[key] == val, f"Champ '{key}' incorrect"

    def test_set_partial_fields(self, open_pdf):
        PDFTools.set_metadata(open_pdf, {"title": "Partiel"})
        meta = PDFTools.get_metadata(open_pdf)
        assert meta["title"] == "Partiel"
        # Other fields should exist (even if empty)
        assert "author" in meta

    def test_metadata_persists_after_save(self, tmp_dir, minimal_pdf):
        """Metadata survives a save/reopen cycle."""
        with pikepdf.open(minimal_pdf) as pdf:
            PDFTools.set_metadata(pdf, {"title": "Persistance"})
            out = str(tmp_dir / "saved.pdf")
            pdf.save(out)
        with pikepdf.open(out) as pdf:
            meta = PDFTools.get_metadata(pdf)
            assert meta["title"] == "Persistance"

    def test_empty_string_clears_field(self, open_pdf):
        PDFTools.set_metadata(open_pdf, {"title": "À effacer"})
        PDFTools.set_metadata(open_pdf, {"title": ""})
        meta = PDFTools.get_metadata(open_pdf)
        assert meta["title"] == ""
