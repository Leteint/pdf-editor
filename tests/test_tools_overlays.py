"""
Tests for PDFTools overlay operations:
watermark, header/footer, text stamp, image stamp.
"""
from __future__ import annotations

import pikepdf
import pytest

from core.tools import PDFTools


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _page_streams(page: pikepdf.Object) -> list[pikepdf.Object]:
    """Return list of content stream objects for a page."""
    existing = page.get("/Contents")
    if existing is None:
        return []
    return list(existing) if isinstance(existing, pikepdf.Array) else [existing]


def _stream_data(obj: pikepdf.Object) -> bytes:
    return bytes(obj.read_bytes())


def _has_marker(page: pikepdf.Object, marker: bytes) -> bool:
    return any(
        _stream_data(s).lstrip().startswith(marker)
        for s in _page_streams(page)
    )


# ---------------------------------------------------------------------------
# Watermark
# ---------------------------------------------------------------------------

class TestWatermark:
    def test_watermark_adds_stream_to_all_pages(self, open_pdf):
        before = [len(_page_streams(p)) for p in open_pdf.pages]
        PDFTools.add_watermark(open_pdf, text="CONFIDENTIEL")
        after  = [len(_page_streams(p)) for p in open_pdf.pages]
        assert all(after[i] > before[i] for i in range(len(before)))

    def test_watermark_text_appears_in_stream(self, open_pdf):
        PDFTools.add_watermark(open_pdf, text="BROUILLON")
        for page in open_pdf.pages:
            combined = b"".join(_stream_data(s) for s in _page_streams(page))
            assert b"BROUILLON" in combined

    def test_watermark_opacity_stored(self, open_pdf):
        PDFTools.add_watermark(open_pdf, text="X", opacity=0.3)
        # ExtGState should exist in resources
        res = open_pdf.pages[0].get("/Resources", pikepdf.Dictionary())
        assert "/ExtGState" in res


# ---------------------------------------------------------------------------
# Header / Footer
# ---------------------------------------------------------------------------

class TestHeaderFooter:
    def test_hf_adds_marker_stream(self, open_pdf):
        PDFTools.add_header_footer(
            open_pdf,
            header=("Gauche", "", ""),
            footer=("", "Pied", ""),
        )
        for page in open_pdf.pages:
            assert _has_marker(page, PDFTools._HF_MARKER)

    def test_hf_skip_first_page(self, open_pdf):
        PDFTools.add_header_footer(
            open_pdf,
            header=("H", "", ""),
            footer=("", "", ""),
            skip_first=True,
        )
        # First page must NOT have HF marker
        assert not _has_marker(open_pdf.pages[0], PDFTools._HF_MARKER)
        # Second page must have it
        assert _has_marker(open_pdf.pages[1], PDFTools._HF_MARKER)

    def test_hf_reapply_does_not_stack(self, open_pdf):
        PDFTools.add_header_footer(open_pdf, header=("A", "", ""), footer=("", "", ""))
        count_after_first = sum(
            1 for s in _page_streams(open_pdf.pages[0])
            if _stream_data(s).lstrip().startswith(PDFTools._HF_MARKER)
        )
        PDFTools.add_header_footer(open_pdf, header=("B", "", ""), footer=("", "", ""))
        count_after_second = sum(
            1 for s in _page_streams(open_pdf.pages[0])
            if _stream_data(s).lstrip().startswith(PDFTools._HF_MARKER)
        )
        assert count_after_second == count_after_first  # replaced, not stacked

    def test_remove_hf_streams(self, open_pdf):
        PDFTools.add_header_footer(open_pdf, header=("X", "", ""), footer=("", "", ""))
        assert _has_marker(open_pdf.pages[0], PDFTools._HF_MARKER)
        PDFTools._remove_hf_streams(open_pdf)
        assert not _has_marker(open_pdf.pages[0], PDFTools._HF_MARKER)

    def test_hf_token_page_resolved(self, open_pdf):
        """Token {page} must appear as '1' (not literally '{page}') in stream."""
        PDFTools.add_header_footer(
            open_pdf,
            header=("{page}", "", ""),
            footer=("", "", ""),
        )
        streams_page0 = _page_streams(open_pdf.pages[0])
        combined = b"".join(_stream_data(s) for s in streams_page0)
        assert b"{page}" not in combined
        assert b"1" in combined

    def test_hf_token_total_resolved(self, open_pdf):
        PDFTools.add_header_footer(
            open_pdf,
            header=("", "{total}", ""),
            footer=("", "", ""),
        )
        combined = b"".join(
            _stream_data(s) for s in _page_streams(open_pdf.pages[0])
        )
        assert b"{total}" not in combined
        assert b"2" in combined  # 2-page PDF


# ---------------------------------------------------------------------------
# Text stamp
# ---------------------------------------------------------------------------

class TestTextStamp:
    def test_stamp_adds_marker_stream(self, open_pdf):
        PDFTools.add_stamp(open_pdf, text="APPROUVÉ")
        for page in open_pdf.pages:
            assert _has_marker(page, PDFTools._STAMP_MARKER)

    def test_stamp_text_in_stream(self, open_pdf):
        PDFTools.add_stamp(open_pdf, text="URGENT")
        combined = b"".join(
            _stream_data(s) for s in _page_streams(open_pdf.pages[0])
        )
        assert b"URGENT" in combined

    def test_stamp_first_page_only(self, open_pdf):
        PDFTools.add_stamp(open_pdf, text="X", pages="first")
        assert _has_marker(open_pdf.pages[0], PDFTools._STAMP_MARKER)
        assert not _has_marker(open_pdf.pages[1], PDFTools._STAMP_MARKER)

    def test_stamp_last_page_only(self, open_pdf):
        PDFTools.add_stamp(open_pdf, text="X", pages="last")
        assert not _has_marker(open_pdf.pages[0], PDFTools._STAMP_MARKER)
        assert _has_marker(open_pdf.pages[1], PDFTools._STAMP_MARKER)

    def test_stamp_reapply_replaces(self, open_pdf):
        PDFTools.add_stamp(open_pdf, text="BROUILLON")
        PDFTools.add_stamp(open_pdf, text="APPROUVÉ")
        markers = [
            s for s in _page_streams(open_pdf.pages[0])
            if _stream_data(s).lstrip().startswith(PDFTools._STAMP_MARKER)
        ]
        assert len(markers) == 1

    def test_remove_stamp_streams(self, open_pdf):
        PDFTools.add_stamp(open_pdf, text="X")
        PDFTools._remove_stamp_streams(open_pdf)
        assert not _has_marker(open_pdf.pages[0], PDFTools._STAMP_MARKER)


# ---------------------------------------------------------------------------
# Image stamp
# ---------------------------------------------------------------------------

class TestImageStamp:
    def test_image_stamp_adds_xobject(self, open_pdf, rgb_png):
        PDFTools.add_image_stamp(open_pdf, image_path=rgb_png)
        res = open_pdf.pages[0].get("/Resources", pikepdf.Dictionary())
        assert "/XObject" in res
        assert "/StampImg" in res["/XObject"]

    def test_image_stamp_rgba_adds_smask(self, open_pdf, rgba_png):
        """PNG with alpha channel should produce an SMask in the XObject."""
        PDFTools.add_image_stamp(open_pdf, image_path=rgba_png)
        res    = open_pdf.pages[0]["/Resources"]
        xobj   = res["/XObject"]["/StampImg"]
        assert "/SMask" in xobj

    def test_image_stamp_rgb_no_smask(self, open_pdf, rgb_png):
        PDFTools.add_image_stamp(open_pdf, image_path=rgb_png)
        res  = open_pdf.pages[0]["/Resources"]
        xobj = res["/XObject"]["/StampImg"]
        assert "/SMask" not in xobj

    def test_image_stamp_jpeg(self, open_pdf, jpeg_img):
        PDFTools.add_image_stamp(open_pdf, image_path=jpeg_img)
        res = open_pdf.pages[0].get("/Resources", pikepdf.Dictionary())
        assert "/StampImg" in res["/XObject"]

    def test_image_stamp_first_page_only(self, open_pdf, rgb_png):
        PDFTools.add_image_stamp(open_pdf, image_path=rgb_png, pages="first")
        res0 = open_pdf.pages[0].get("/Resources", pikepdf.Dictionary())
        res1 = open_pdf.pages[1].get("/Resources", pikepdf.Dictionary())
        assert "/XObject" in res0
        assert "/XObject" not in res1

    def test_image_stamp_opacity_extgstate(self, open_pdf, rgb_png):
        PDFTools.add_image_stamp(open_pdf, image_path=rgb_png, opacity=0.5)
        res = open_pdf.pages[0]["/Resources"]
        assert "/ExtGState" in res
        assert "/GSimg" in res["/ExtGState"]

    def test_image_stamp_content_stream_placed(self, open_pdf, rgb_png):
        """The content stream must reference /StampImg via the Do operator."""
        PDFTools.add_image_stamp(open_pdf, image_path=rgb_png)
        combined = b"".join(
            _stream_data(s) for s in _page_streams(open_pdf.pages[0])
        )
        assert b"/StampImg Do" in combined
