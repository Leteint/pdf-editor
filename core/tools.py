"""
PDF utility tools: merge, split, rotate, extract text/images.
"""
from __future__ import annotations

import os
from typing import Optional
import pikepdf
from pypdf import PdfReader, PdfWriter


class PDFTools:
    """Stateless utility class — all methods work on file paths or pikepdf objects."""

    # ------------------------------------------------------------------
    # Merge
    # ------------------------------------------------------------------

    @staticmethod
    def merge(input_paths: list[str], output_path: str) -> None:
        """Merge multiple PDF files into one."""
        writer = PdfWriter()
        for path in input_paths:
            reader = PdfReader(path)
            for page in reader.pages:
                writer.add_page(page)
        with open(output_path, "wb") as f:
            writer.write(f)

    # ------------------------------------------------------------------
    # Split
    # ------------------------------------------------------------------

    @staticmethod
    def split_all(input_path: str, output_dir: str) -> list[str]:
        """Split each page into a separate PDF. Returns list of output paths."""
        os.makedirs(output_dir, exist_ok=True)
        reader = PdfReader(input_path)
        basename = os.path.splitext(os.path.basename(input_path))[0]
        output_paths = []
        for i, page in enumerate(reader.pages):
            writer = PdfWriter()
            writer.add_page(page)
            out = os.path.join(output_dir, f"{basename}_page_{i + 1:04d}.pdf")
            with open(out, "wb") as f:
                writer.write(f)
            output_paths.append(out)
        return output_paths

    @staticmethod
    def split_range(
        input_path: str,
        output_path: str,
        start: int,
        end: int,
    ) -> None:
        """Extract pages [start, end] (0-based inclusive) into a new PDF."""
        reader = PdfReader(input_path)
        writer = PdfWriter()
        for i in range(start, min(end + 1, len(reader.pages))):
            writer.add_page(reader.pages[i])
        with open(output_path, "wb") as f:
            writer.write(f)

    @staticmethod
    def split_by_chunk(input_path: str, output_dir: str, pages_per_chunk: int) -> list[str]:
        """Split the PDF into chunks of *pages_per_chunk* pages each.

        Example: 10-page PDF with pages_per_chunk=3 →
            _part_001.pdf (p1-3), _part_002.pdf (p4-6),
            _part_003.pdf (p7-9), _part_004.pdf (p10)
        Returns the list of created file paths.
        """
        os.makedirs(output_dir, exist_ok=True)
        reader = PdfReader(input_path)
        total = len(reader.pages)
        basename = os.path.splitext(os.path.basename(input_path))[0]
        output_paths = []
        chunk_idx = 1
        for start in range(0, total, pages_per_chunk):
            writer = PdfWriter()
            for i in range(start, min(start + pages_per_chunk, total)):
                writer.add_page(reader.pages[i])
            out = os.path.join(output_dir, f"{basename}_part_{chunk_idx:03d}.pdf")
            with open(out, "wb") as fh:
                writer.write(fh)
            output_paths.append(out)
            chunk_idx += 1
        return output_paths

    # ------------------------------------------------------------------
    # Reorder / reorganize pages
    # ------------------------------------------------------------------

    @staticmethod
    def reorder_pages(
        pdf: pikepdf.Pdf,
        page_specs: list[tuple],
    ) -> None:
        """Reorganise pages of an already-open pikepdf.Pdf in-place.

        Args:
            pdf:        open pikepdf document (modified in-place).
            page_specs: ordered list of (source_path, orig_idx, extra_rot) where
                        source_path is None for the current document or a file path
                        for an external PDF to import pages from.
        """
        import io as _io

        # Serialise the original document to a buffer so we can read its pages
        # independently after clearing pdf.pages (page objects become invalid
        # once removed from the pages array).
        buf = _io.BytesIO()
        pdf.save(buf)
        buf.seek(0)
        original = pikepdf.open(buf)

        # Open external PDFs once (keyed by path)
        ext_cache: dict[str, pikepdf.Pdf] = {}
        for source, _idx, _rot in page_specs:
            if source is not None and source not in ext_cache:
                ext_cache[source] = pikepdf.open(source)

        # Clear the document pages
        while len(pdf.pages) > 0:
            del pdf.pages[0]

        # Append pages in desired order — pikepdf.pages.append() handles
        # cross-document import automatically via the pages interface.
        for source, idx, rot in page_specs:
            src_pdf = original if source is None else ext_cache[source]
            pdf.pages.append(src_pdf.pages[idx])
            if rot % 360 != 0:
                page = pdf.pages[-1]
                current = int(page.get("/Rotate", 0))
                page["/Rotate"] = pikepdf.Integer((current + rot) % 360)

        original.close()
        for ext_pdf in ext_cache.values():
            ext_pdf.close()

    # ------------------------------------------------------------------
    # Rotate pages
    # ------------------------------------------------------------------

    @staticmethod
    def rotate_pages(
        input_path: str,
        output_path: str,
        degrees: int,
        pages: Optional[list[int]] = None,
    ) -> None:
        """Rotate specific pages (or all if pages=None) by degrees."""
        reader = PdfReader(input_path)
        writer = PdfWriter()
        for i, page in enumerate(reader.pages):
            if pages is None or i in pages:
                page.rotate(degrees)
            writer.add_page(page)
        with open(output_path, "wb") as f:
            writer.write(f)

    # ------------------------------------------------------------------
    # Watermark
    # ------------------------------------------------------------------

    @staticmethod
    def add_watermark(
        pdf: pikepdf.Pdf,
        text: str,
        opacity: float = 0.25,
        font_size: int = 60,
        color: tuple = (0.6, 0.6, 0.6),
    ) -> None:
        """Stamp a diagonal text watermark on every page of *pdf* (in-place).

        Args:
            pdf:       open pikepdf document.
            text:      watermark string (ASCII/Latin-1).
            opacity:   0.0 (invisible) → 1.0 (opaque).
            font_size: point size of the watermark text.
            color:     (r, g, b) each 0.0–1.0.
        """
        import math

        # Sanitise text for PDF string (Latin-1; strip unsupported chars)
        safe_text = text.encode("latin-1", errors="replace").decode("latin-1")
        safe_text = safe_text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

        r, g, b = color
        angle = 45.0
        rad   = math.radians(angle)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        # Approximate char width for Helvetica ≈ 0.55 × font_size
        text_w = len(text) * font_size * 0.55

        for page in pdf.pages:
            mb  = page.get("/MediaBox", pikepdf.Array([0, 0, 595, 842]))
            pw  = float(mb[2]) - float(mb[0])
            ph  = float(mb[3]) - float(mb[1])
            cx  = pw / 2
            cy  = ph / 2
            # Offset so the text is centred at the page centre
            tx  = cx - (text_w / 2) * cos_a + (font_size * 0.25) * sin_a
            ty  = cy - (text_w / 2) * sin_a - (font_size * 0.25) * cos_a

            # Ensure Resources dict exists
            if "/Resources" not in page:
                page["/Resources"] = pikepdf.Dictionary()
            res = page["/Resources"]

            # Register Helvetica font
            if "/Font" not in res:
                res["/Font"] = pikepdf.Dictionary()
            if "/WMFont" not in res["/Font"]:
                res["/Font"]["/WMFont"] = pdf.make_indirect(pikepdf.Dictionary(
                    Type=pikepdf.Name.Font,
                    Subtype=pikepdf.Name.Type1,
                    BaseFont=pikepdf.Name.Helvetica,
                    Encoding=pikepdf.Name.WinAnsiEncoding,
                ))

            # Register ExtGState for fill+stroke opacity
            if "/ExtGState" not in res:
                res["/ExtGState"] = pikepdf.Dictionary()
            res["/ExtGState"]["/WMgs"] = pdf.make_indirect(pikepdf.Dictionary(
                Type=pikepdf.Name.ExtGState,
                ca=pikepdf.Real(round(opacity, 3)),   # fill opacity
                CA=pikepdf.Real(round(opacity, 3)),   # stroke opacity
            ))

            # Build watermark content stream
            wm_stream = (
                f"q\n"
                f"/WMgs gs\n"
                f"{r:.3f} {g:.3f} {b:.3f} rg\n"
                f"BT\n"
                f"/WMFont {font_size} Tf\n"
                f"{cos_a:.4f} {sin_a:.4f} {-sin_a:.4f} {cos_a:.4f} "
                f"{tx:.2f} {ty:.2f} Tm\n"
                f"({safe_text}) Tj\n"
                f"ET\n"
                f"Q\n"
            ).encode("latin-1")

            wm_obj = pdf.make_stream(wm_stream)

            # Append watermark after existing content (renders on top but semi-transparent)
            existing = page.get("/Contents")
            if existing is None:
                page["/Contents"] = wm_obj
            elif isinstance(existing, pikepdf.Array):
                existing.append(wm_obj)
            else:
                page["/Contents"] = pikepdf.Array([existing, wm_obj])

    # ------------------------------------------------------------------
    # Headers / Footers
    # ------------------------------------------------------------------

    # Marker embedded in every HF content stream so it can be identified and removed on re-apply
    _HF_MARKER = b"% PDF-EDITOR-HF\n"

    @staticmethod
    def _remove_hf_streams(pdf: pikepdf.Pdf) -> None:
        """Remove all previously injected header/footer streams from every page."""
        marker = PDFTools._HF_MARKER
        for page in pdf.pages:
            existing = page.get("/Contents")
            if existing is None:
                continue
            refs = list(existing) if isinstance(existing, pikepdf.Array) else [existing]
            kept = []
            for obj in refs:
                try:
                    data = bytes(obj.read_bytes())
                    if data.lstrip().startswith(marker):
                        continue  # drop this HF stream
                except Exception:
                    pass
                kept.append(obj)
            if len(kept) == len(refs):
                continue  # nothing removed
            if not kept:
                page["/Contents"] = pikepdf.Array([])
            elif len(kept) == 1:
                page["/Contents"] = kept[0]
            else:
                page["/Contents"] = pikepdf.Array(kept)

    @staticmethod
    def add_header_footer(
        pdf: pikepdf.Pdf,
        header: tuple[str, str, str],
        footer: tuple[str, str, str],
        font_size: int = 10,
        color: tuple = (0.0, 0.0, 0.0),
        margin_mm: float = 15.0,
        skip_first: bool = False,
    ) -> None:
        """Add header/footer text to every page of *pdf* (in-place).

        Each of *header* and *footer* is a (left, centre, right) tuple.
        Tokens in the text strings:
            {page}  → current 1-based page number
            {total} → total page count
            {date}  → today's date (YYYY-MM-DD)
        """
        import datetime

        # Remove any previously injected HF streams before re-applying
        PDFTools._remove_hf_streams(pdf)

        today      = datetime.date.today().strftime("%d/%m/%Y")
        total      = len(pdf.pages)
        r, g, b    = color
        # 1 mm ≈ 2.8346 PDF units (1 pt)
        margin_pt  = margin_mm * 2.8346
        # Approximate Helvetica avg char width at font_size
        char_w     = font_size * 0.55

        def _resolve(text: str, page_num: int) -> str:
            return (text
                    .replace("{page}",  str(page_num))
                    .replace("{total}", str(total))
                    .replace("{date}",  today))

        def _safe(text: str) -> str:
            return (text
                    .encode("latin-1", errors="replace")
                    .decode("latin-1")
                    .replace("\\", "\\\\")
                    .replace("(", "\\(")
                    .replace(")", "\\)"))

        def _text_w(text: str) -> float:
            return len(text) * char_w

        def _text_block(text: str, x: float, y: float) -> str:
            """One BT/ET block with absolute position via Tm."""
            return (
                f"BT\n"
                f"/HFFont {font_size} Tf\n"
                f"1 0 0 1 {x:.2f} {y:.2f} Tm\n"
                f"({_safe(text)}) Tj\n"
                f"ET\n"
            )

        def _stream_for_zone(
            left: str, center: str, right: str,
            y: float, pw: float,
        ) -> str:
            """Build PDF content stream for one header/footer line.
            Each field gets its own BT/ET with absolute Tm positioning."""
            blocks = []

            if left.strip():
                blocks.append(_text_block(left, margin_pt, y))

            if center.strip():
                x = max(0.0, pw / 2 - _text_w(center) / 2)
                blocks.append(_text_block(center, x, y))

            if right.strip():
                x = max(0.0, pw - margin_pt - _text_w(right))
                blocks.append(_text_block(right, x, y))

            if not blocks:
                return ""

            return (
                f"q\n"
                f"{r:.3f} {g:.3f} {b:.3f} rg\n"
                + "".join(blocks) +
                f"Q\n"
            )

        for page_idx, page in enumerate(pdf.pages):
            if skip_first and page_idx == 0:
                continue

            page_num = page_idx + 1
            mb  = page.get("/MediaBox", pikepdf.Array([0, 0, 595, 842]))
            pw  = float(mb[2]) - float(mb[0])
            ph  = float(mb[3]) - float(mb[1])

            # Header y: near top  —  Footer y: near bottom
            hdr_y = ph - margin_pt - font_size
            ftr_y = margin_pt

            # Resolve tokens
            hl, hc, hr = [_resolve(t, page_num) for t in header]
            fl, fc, fr = [_resolve(t, page_num) for t in footer]

            hdr_stream = _stream_for_zone(hl, hc, hr, hdr_y, pw)
            ftr_stream = _stream_for_zone(fl, fc, fr, ftr_y, pw)
            # Prefix with marker so this stream can be identified and removed later
            combined   = PDFTools._HF_MARKER + (hdr_stream + ftr_stream).encode("latin-1")

            if not combined.strip():
                continue

            # Ensure Resources
            if "/Resources" not in page:
                page["/Resources"] = pikepdf.Dictionary()
            res = page["/Resources"]
            if "/Font" not in res:
                res["/Font"] = pikepdf.Dictionary()
            if "/HFFont" not in res["/Font"]:
                res["/Font"]["/HFFont"] = pdf.make_indirect(pikepdf.Dictionary(
                    Type=pikepdf.Name.Font,
                    Subtype=pikepdf.Name.Type1,
                    BaseFont=pikepdf.Name.Helvetica,
                    Encoding=pikepdf.Name.WinAnsiEncoding,
                ))

            hf_obj = pdf.make_stream(combined)
            existing = page.get("/Contents")
            if existing is None:
                page["/Contents"] = hf_obj
            elif isinstance(existing, pikepdf.Array):
                existing.append(hf_obj)
            else:
                page["/Contents"] = pikepdf.Array([existing, hf_obj])

    # ------------------------------------------------------------------
    # Stamps
    # ------------------------------------------------------------------

    _STAMP_MARKER = b"% PDF-EDITOR-STAMP\n"

    @staticmethod
    def _remove_stamp_streams(pdf: pikepdf.Pdf) -> None:
        """Remove all previously injected stamp streams from every page."""
        marker = PDFTools._STAMP_MARKER
        for page in pdf.pages:
            existing = page.get("/Contents")
            if existing is None:
                continue
            refs = list(existing) if isinstance(existing, pikepdf.Array) else [existing]
            kept = []
            for obj in refs:
                try:
                    data = bytes(obj.read_bytes())
                    if data.lstrip().startswith(marker):
                        continue
                except Exception:
                    pass
                kept.append(obj)
            if len(kept) == len(refs):
                continue
            if not kept:
                page["/Contents"] = pikepdf.Array([])
            elif len(kept) == 1:
                page["/Contents"] = kept[0]
            else:
                page["/Contents"] = pikepdf.Array(kept)

    @staticmethod
    def add_stamp(
        pdf: pikepdf.Pdf,
        text: str,
        color: tuple = (0.05, 0.55, 0.10),
        position: str = "top-right",
        pages: str = "all",
        opacity: float = 0.80,
        rotation: int = 0,
    ) -> None:
        """Add a rubber-stamp overlay to pages (in-place).

        position : 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left' | 'center'
        pages    : 'all' | 'first' | 'last'
        rotation : 0 | -45
        """
        import math as _math

        # Remove any previous stamp first
        PDFTools._remove_stamp_streams(pdf)

        r, g, b = color
        total   = len(pdf.pages)

        # Font metrics (Helvetica-Bold approximation)
        font_size = 22
        char_w    = font_size * 0.65
        text_w    = len(text) * char_w
        pad       = 11.0
        lw        = 2.5          # border line width
        box_w     = text_w + 2 * pad
        box_h     = font_size + 2 * pad
        half_w    = box_w / 2
        half_h    = box_h / 2
        # Approximate baseline offset to visually center text in box
        base_y    = -font_size * 0.28

        # Rotation matrix
        angle = _math.radians(rotation)
        cos_a, sin_a = _math.cos(angle), _math.sin(angle)

        def _safe(t: str) -> str:
            return (t.encode("latin-1", errors="replace").decode("latin-1")
                    .replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)"))

        def _build_stream(pw: float, ph: float) -> bytes:
            edge = 30.0  # margin from page edge (pt)
            if rotation != 0:
                # Diagonal stamps always centred
                cx, cy = pw / 2, ph / 2
            else:
                if position == "top-right":
                    cx, cy = pw - edge - half_w, ph - edge - half_h
                elif position == "top-left":
                    cx, cy = edge + half_w,      ph - edge - half_h
                elif position == "bottom-right":
                    cx, cy = pw - edge - half_w, edge + half_h
                elif position == "bottom-left":
                    cx, cy = edge + half_w,      edge + half_h
                else:  # center
                    cx, cy = pw / 2, ph / 2

            stream = (
                f"% PDF-EDITOR-STAMP\n"          # marker (decoded below)
                f"q\n"
                f"/GSstamp gs\n"
                # translate + rotate
                f"{cos_a:.5f} {sin_a:.5f} {-sin_a:.5f} {cos_a:.5f} "
                f"{cx:.2f} {cy:.2f} cm\n"
                # very light fill (10 % of color mixed into white)
                f"{1-(1-r)*0.12:.3f} {1-(1-g)*0.12:.3f} {1-(1-b)*0.12:.3f} rg\n"
                f"{-half_w:.2f} {-half_h:.2f} {box_w:.2f} {box_h:.2f} re f\n"
                # border
                f"{r:.3f} {g:.3f} {b:.3f} RG\n"
                f"{lw:.1f} w\n"
                f"{-half_w:.2f} {-half_h:.2f} {box_w:.2f} {box_h:.2f} re S\n"
                # inner border (double-line effect, 1pt inside)
                f"{-half_w+lw:.2f} {-half_h+lw:.2f} "
                f"{box_w-2*lw:.2f} {box_h-2*lw:.2f} re S\n"
                # text
                f"{r:.3f} {g:.3f} {b:.3f} rg\n"
                f"BT\n"
                f"/StampFont {font_size} Tf\n"
                f"{-text_w/2:.2f} {base_y:.2f} Td\n"
                f"({_safe(text)}) Tj\n"
                f"ET\n"
                f"Q\n"
            )
            return stream.encode("latin-1")

        def _ensure_resources(page: pikepdf.Object) -> None:
            if "/Resources" not in page:
                page["/Resources"] = pikepdf.Dictionary()
            res = page["/Resources"]
            # Font
            if "/Font" not in res:
                res["/Font"] = pikepdf.Dictionary()
            if "/StampFont" not in res["/Font"]:
                res["/Font"]["/StampFont"] = pdf.make_indirect(pikepdf.Dictionary(
                    Type=pikepdf.Name.Font,
                    Subtype=pikepdf.Name.Type1,
                    BaseFont=pikepdf.Name("/Helvetica-Bold"),
                    Encoding=pikepdf.Name.WinAnsiEncoding,
                ))
            # ExtGState for opacity
            if "/ExtGState" not in res:
                res["/ExtGState"] = pikepdf.Dictionary()
            if "/GSstamp" not in res["/ExtGState"]:
                res["/ExtGState"]["/GSstamp"] = pdf.make_indirect(pikepdf.Dictionary(
                    Type=pikepdf.Name.ExtGState,
                    ca=opacity,   # fill alpha
                    CA=opacity,   # stroke alpha
                ))

        for idx, page in enumerate(pdf.pages):
            if pages == "first"  and idx != 0:
                continue
            if pages == "last"   and idx != total - 1:
                continue

            mb = page.get("/MediaBox", pikepdf.Array([0, 0, 595, 842]))
            pw = float(mb[2]) - float(mb[0])
            ph = float(mb[3]) - float(mb[1])

            _ensure_resources(page)

            stamp_obj = pdf.make_stream(_build_stream(pw, ph))
            existing  = page.get("/Contents")
            if existing is None:
                page["/Contents"] = stamp_obj
            elif isinstance(existing, pikepdf.Array):
                existing.append(stamp_obj)
            else:
                page["/Contents"] = pikepdf.Array([existing, stamp_obj])

    # ------------------------------------------------------------------
    # Image stamps
    # ------------------------------------------------------------------

    @staticmethod
    def add_image_stamp(
        pdf: pikepdf.Pdf,
        image_path: str,
        position: str = "bottom-right",
        pages: str = "all",
        scale_pct: int = 25,
        opacity: float = 1.0,
    ) -> None:
        """Embed an image stamp (logo, signature…) on selected pages.

        scale_pct : stamp width as a percentage of the page width.
        opacity   : 0.0–1.0 (1.0 = fully opaque).
        position  : 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left' | 'center'
        pages     : 'all' | 'first' | 'last'
        """
        import zlib as _zlib
        from PIL import Image as _Image

        total = len(pdf.pages)

        # ── Build PDF image XObject (with transparency support) ──────────
        with _Image.open(image_path) as img:
            has_alpha = img.mode in ("RGBA", "LA") or (
                img.mode == "P" and "transparency" in img.info
            )
            img_rgb = img.convert("RGBA" if has_alpha else "RGB")
            img_w, img_h = img_rgb.size

            if has_alpha:
                r, g, b, a = img_rgb.split()
                rgb_bytes   = _Image.merge("RGB", (r, g, b)).tobytes()
                alpha_bytes = a.tobytes()

                smask_stream = pdf.make_stream(_zlib.compress(alpha_bytes, 6))
                smask_stream["/Type"]             = pikepdf.Name.XObject
                smask_stream["/Subtype"]          = pikepdf.Name.Image
                smask_stream["/Width"]            = img_w
                smask_stream["/Height"]           = img_h
                smask_stream["/ColorSpace"]       = pikepdf.Name.DeviceGray
                smask_stream["/BitsPerComponent"] = 8
                smask_stream["/Filter"]           = pikepdf.Name.FlateDecode
                smask_ref = pdf.make_indirect(smask_stream)

                xobj = pdf.make_stream(_zlib.compress(rgb_bytes, 6))
                xobj["/SMask"] = smask_ref
            else:
                rgb_bytes = img_rgb.tobytes()
                xobj = pdf.make_stream(_zlib.compress(rgb_bytes, 6))

            xobj["/Type"]             = pikepdf.Name.XObject
            xobj["/Subtype"]          = pikepdf.Name.Image
            xobj["/Width"]            = img_w
            xobj["/Height"]           = img_h
            xobj["/ColorSpace"]       = pikepdf.Name.DeviceRGB
            xobj["/BitsPerComponent"] = 8
            xobj["/Filter"]           = pikepdf.Name.FlateDecode
            xobj_ref = pdf.make_indirect(xobj)

        edge = 20.0  # margin from page edge (pt)

        for idx, page in enumerate(pdf.pages):
            if pages == "first" and idx != 0:
                continue
            if pages == "last"  and idx != total - 1:
                continue

            mb = page.get("/MediaBox", pikepdf.Array([0, 0, 595, 842]))
            pw = float(mb[2]) - float(mb[0])
            ph = float(mb[3]) - float(mb[1])

            # Stamp size (maintain aspect ratio)
            sw = pw * scale_pct / 100.0
            sh = sw * img_h / max(img_w, 1)

            # Lower-left corner of stamp
            if position == "bottom-right":
                sx, sy = pw - edge - sw, edge
            elif position == "bottom-left":
                sx, sy = edge, edge
            elif position == "top-right":
                sx, sy = pw - edge - sw, ph - edge - sh
            elif position == "top-left":
                sx, sy = edge, ph - edge - sh
            else:  # center
                sx, sy = (pw - sw) / 2, (ph - sh) / 2

            # ── Ensure Resources ────────────────────────────────────────
            if "/Resources" not in page:
                page["/Resources"] = pikepdf.Dictionary()
            res = page["/Resources"]
            if "/XObject" not in res:
                res["/XObject"] = pikepdf.Dictionary()
            res["/XObject"]["/StampImg"] = xobj_ref

            if "/ExtGState" not in res:
                res["/ExtGState"] = pikepdf.Dictionary()
            if "/GSimg" not in res["/ExtGState"]:
                res["/ExtGState"]["/GSimg"] = pdf.make_indirect(pikepdf.Dictionary(
                    Type=pikepdf.Name.ExtGState,
                    ca=opacity,
                    CA=opacity,
                ))

            # ── Content stream ───────────────────────────────────────────
            stream = (
                f"q\n"
                f"/GSimg gs\n"
                f"{sw:.4f} 0 0 {sh:.4f} {sx:.4f} {sy:.4f} cm\n"
                f"/StampImg Do\n"
                f"Q\n"
            ).encode("latin-1")

            stamp_obj = pdf.make_stream(stream)
            existing  = page.get("/Contents")
            if existing is None:
                page["/Contents"] = stamp_obj
            elif isinstance(existing, pikepdf.Array):
                existing.append(stamp_obj)
            else:
                page["/Contents"] = pikepdf.Array([existing, stamp_obj])

    # ------------------------------------------------------------------
    # Compress
    # ------------------------------------------------------------------

    @staticmethod
    def compress(pdf: pikepdf.Pdf) -> int:
        """Compress *pdf* in-place using object streams and content reuse.

        Returns the estimated byte saving (before - after serialised size).
        The caller is responsible for saving the document afterwards.
        """
        import io as _io

        # Measure before
        buf_before = _io.BytesIO()
        pdf.save(buf_before)
        size_before = buf_before.tell()

        # Re-save with maximum compression options:
        #   object_stream_mode=2  → pack indirect objects into compressed streams
        #   recompress_flate=True → re-compress already-compressed streams
        #   deterministic_id=True → stable IDs (smaller diff for incremental saves)
        buf_after = _io.BytesIO()
        pdf.save(
            buf_after,
            object_stream_mode=pikepdf.ObjectStreamMode.generate,
            recompress_flate=True,
            deterministic_id=True,
        )
        size_after = buf_after.tell()
        saving = size_before - size_after

        # If the result is actually smaller, reload the pdf from the compressed bytes
        if saving > 0:
            buf_after.seek(0)
            compressed = pikepdf.open(buf_after)
            # Replace pages and objects in-place
            while len(pdf.pages) > 0:
                del pdf.pages[0]
            for page in compressed.pages:
                pdf.pages.append(page)
            # Copy root/info
            if "/Info" in compressed.docinfo:
                pdf.docinfo.update(compressed.docinfo)
            compressed.close()

        return max(saving, 0)

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    @staticmethod
    def get_metadata(pdf: pikepdf.Pdf) -> dict:
        """Return a dict with the standard PDF metadata fields."""
        info = pdf.docinfo
        return {
            "title":    str(info.get("/Title",    "") or ""),
            "author":   str(info.get("/Author",   "") or ""),
            "subject":  str(info.get("/Subject",  "") or ""),
            "keywords": str(info.get("/Keywords", "") or ""),
            "creator":  str(info.get("/Creator",  "") or ""),
        }

    @staticmethod
    def set_metadata(pdf: pikepdf.Pdf, meta: dict) -> None:
        """Write standard metadata fields into *pdf* (in-place)."""
        # PDF info-dictionary keys (universally supported by all viewers)
        docinfo_map = {
            "title":    "/Title",
            "author":   "/Author",
            "subject":  "/Subject",
            "keywords": "/Keywords",
            "creator":  "/Creator",
        }
        # XMP namespace keys (correct per ISO 16684 / Adobe XMP spec)
        xmp_map = {
            "title":    "dc:title",
            "author":   "dc:creator",
            "subject":  "dc:description",
            "keywords": "pdf:Keywords",
            "creator":  "xmp:CreatorTool",
        }
        # XMP fields that require a list value instead of a plain string
        _list_fields = {"dc:creator"}

        with pdf.open_metadata() as m:
            for key, pdf_key in docinfo_map.items():
                value = meta.get(key, "").strip()
                xmp_key = xmp_map[key]
                if value:
                    pdf.docinfo[pdf_key] = pikepdf.String(value)
                    m[xmp_key] = [value] if xmp_key in _list_fields else value
                else:
                    try:
                        del pdf.docinfo[pdf_key]
                    except (KeyError, AttributeError):
                        pass
                    m.pop(xmp_key, None)

    # ------------------------------------------------------------------
    # Extract text
    # ------------------------------------------------------------------

    @staticmethod
    def extract_text(input_path: str, page_range: Optional[tuple[int, int]] = None) -> str:
        """Extract text from PDF. Optionally restrict to page_range (start, end) 0-based."""
        try:
            import pdfplumber
            with pdfplumber.open(input_path) as pdf:
                pages = pdf.pages
                if page_range:
                    pages = pages[page_range[0]: page_range[1] + 1]
                return "\n\n".join(p.extract_text() or "" for p in pages)
        except ImportError:
            reader = PdfReader(input_path)
            pages = reader.pages
            if page_range:
                pages = pages[page_range[0]: page_range[1] + 1]
            return "\n\n".join(p.extract_text() or "" for p in pages)

    # ------------------------------------------------------------------
    # Extract images
    # ------------------------------------------------------------------

    @staticmethod
    def extract_images(input_path: str, output_dir: str) -> list[str]:
        """Extract all embedded images. Returns list of saved file paths."""
        os.makedirs(output_dir, exist_ok=True)
        reader = PdfReader(input_path)
        saved = []
        count = 0
        for page_num, page in enumerate(reader.pages):
            for img_name, img_obj in page.images.items():
                ext = "png"
                out_path = os.path.join(output_dir, f"page{page_num + 1}_{count:04d}.{ext}")
                with open(out_path, "wb") as f:
                    f.write(img_obj.data)
                saved.append(out_path)
                count += 1
        return saved

    # ------------------------------------------------------------------
    # Protect / Unlock
    # ------------------------------------------------------------------

    @staticmethod
    def protect(input_path: str, output_path: str, owner_password: str) -> None:
        """
        Protect with an owner (permissions) password only.
        The file can still be opened and viewed without a password,
        but modifications require the owner password.
        """
        reader = PdfReader(input_path)
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        # user_password="" → viewable by anyone; owner_password → required to modify
        writer.encrypt(user_password="", owner_password=owner_password)
        with open(output_path, "wb") as f:
            writer.write(f)

    @staticmethod
    def unlock(input_path: str, output_path: str, password: str) -> None:
        reader = PdfReader(input_path)
        if reader.is_encrypted:
            reader.decrypt(password)
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        with open(output_path, "wb") as f:
            writer.write(f)

    # ------------------------------------------------------------------
    # Text-at-position (for inline editing)
    # ------------------------------------------------------------------

    @staticmethod
    def get_word_at_position(
        pdf_path: str,
        page_index: int,
        norm_x: float,
        norm_y: float,
    ) -> Optional[dict]:
        """
        Find the word (or line) under (norm_x, norm_y) on the given page.
        Returns a dict with:
          text, norm_rect (QRectF-ready dict with x/y/w/h),
          font_name, font_size, bold, italic, color
        or None if nothing found.
        pdfplumber coordinate origin: top-left, same as our normalized system.
        pdf_path must be a real file path (always — caller writes temp file if needed).
        """
        try:
            import pdfplumber
            with pdfplumber.open(pdf_path) as pdf:
                if page_index >= len(pdf.pages):
                    return None
                page = pdf.pages[page_index]
                pw, ph = page.width, page.height

                # Click position in PDF units
                click_x = norm_x * pw
                click_y = norm_y * ph

                # Try to find the word under the cursor
                words = page.extract_words(
                    extra_attrs=["fontname", "size", "stroking_color", "non_stroking_color"],
                    use_text_flow=True,
                )
                best = None
                for word in words:
                    x0, top, x1, bottom = word["x0"], word["top"], word["x1"], word["bottom"]
                    # Expand hit area slightly for easier clicking
                    if x0 - 2 <= click_x <= x1 + 2 and top - 2 <= click_y <= bottom + 2:
                        best = word
                        break

                if best is None:
                    # Fallback: find the closest word
                    def dist(w):
                        cx = (w["x0"] + w["x1"]) / 2
                        cy = (w["top"] + w["bottom"]) / 2
                        return (cx - click_x) ** 2 + (cy - click_y) ** 2
                    candidates = [w for w in words if w.get("text", "").strip()]
                    if candidates:
                        best = min(candidates, key=dist)
                        # Only accept if reasonably close (within 50 PDF units)
                        if dist(best) > 50 ** 2:
                            best = None

                if best is None:
                    return None

                # Expand to adjacent words on the same baseline, but stop at large
                # gaps (tab stops, column separators) so only one text block is selected.
                if best is not None:
                    b_top    = best["top"]
                    b_bottom = best["bottom"]
                    b_height = max(1, b_bottom - b_top)
                    tol      = b_height * 0.6
                    line = [
                        w for w in words
                        if abs((w["top"] + w["bottom"]) / 2 - (b_top + b_bottom) / 2) < tol
                        and w.get("text", "").strip()
                    ]
                    line.sort(key=lambda w: w["x0"])
                    if len(line) > 1:
                        # Locate the clicked word within the sorted line
                        best_cx  = (best["x0"] + best["x1"]) / 2
                        best_idx = min(range(len(line)),
                                       key=lambda i: abs((line[i]["x0"] + line[i]["x1"]) / 2 - best_cx))
                        # Stop extending when gap exceeds 1.5× line height (tab / column boundary)
                        max_gap = b_height * 1.5
                        left_idx = best_idx
                        for i in range(best_idx - 1, -1, -1):
                            if line[i + 1]["x0"] - line[i]["x1"] <= max_gap:
                                left_idx = i
                            else:
                                break
                        right_idx = best_idx
                        for i in range(best_idx + 1, len(line)):
                            if line[i]["x0"] - line[i - 1]["x1"] <= max_gap:
                                right_idx = i
                            else:
                                break
                        segment = line[left_idx : right_idx + 1]
                        if len(segment) > 1:
                            best = dict(best)
                            best["text"]   = " ".join(w["text"] for w in segment)
                            best["x0"]     = min(w["x0"]     for w in segment)
                            best["x1"]     = max(w["x1"]     for w in segment)
                            best["top"]    = min(w["top"]    for w in segment)
                            best["bottom"] = max(w["bottom"] for w in segment)

                font_name = best.get("fontname", "") or ""
                font_size = float(best.get("size", 12) or 12)
                text = best.get("text", "")

                # Detect bold/italic from font name conventions
                fn_lower = font_name.lower()
                bold = "bold" in fn_lower or ",b" in fn_lower or "-bold" in fn_lower
                italic = (
                    "italic" in fn_lower or "oblique" in fn_lower
                    or ",i" in fn_lower or "-it" in fn_lower
                )

                # Clean font family name (strip subset prefix like "ABCDEF+")
                family = font_name.split("+")[-1] if "+" in font_name else font_name
                for suffix in ["-Bold", "-Italic", "-BoldItalic", "-Regular",
                               ",Bold", ",Italic", ",BoldItalic"]:
                    family = family.replace(suffix, "").replace(suffix.lower(), "")

                # Color (non_stroking = fill color, most common for text)
                color = best.get("non_stroking_color")
                hex_color = "#000000"
                if isinstance(color, (list, tuple)):
                    if len(color) == 3:
                        hex_color = "#{:02x}{:02x}{:02x}".format(
                            int(color[0] * 255), int(color[1] * 255), int(color[2] * 255)
                        )
                    elif len(color) == 1:
                        g = int(color[0] * 255)
                        hex_color = "#{:02x}{:02x}{:02x}".format(g, g, g)

                return {
                    "text": text,
                    "norm_rect": {
                        "x": best["x0"] / pw,
                        "y": best["top"] / ph,
                        "width": (best["x1"] - best["x0"]) / pw,
                        "height": (best["bottom"] - best["top"]) / ph,
                    },
                    "font_name": font_name,
                    "font_family": family.strip() or "Arial",
                    "font_size": font_size,
                    "bold": bold,
                    "italic": italic,
                    "color": hex_color,
                }
        except Exception:
            return None

    # ------------------------------------------------------------------
    # Image manipulation
    # ------------------------------------------------------------------

    @staticmethod
    def get_images_on_page(pdf_path: str, page_index: int) -> list[dict]:
        """
        Return list of images on the page with normalized bounding boxes.
        Each dict: {name, x, y, width, height}  (all coords 0-1 normalized)

        Uses pikepdf to parse the content stream (reliable for images placed
        via q/cm/Do/Q), then merges with pdfplumber results for any extras.
        """
        result = PDFTools._get_images_via_pikepdf(pdf_path, page_index)
        seen_names = {r["name"] for r in result}

        # Merge pdfplumber detections not already found via pikepdf
        try:
            import pdfplumber
            with pdfplumber.open(pdf_path) as pdf:
                if page_index < len(pdf.pages):
                    page = pdf.pages[page_index]
                    pw, ph = page.width, page.height
                    for img in page.images:
                        name = img.get("name", "")
                        if name in seen_names:
                            continue
                        x0 = img.get("x0", 0)
                        y0 = img.get("top", 0)
                        x1 = img.get("x1", 0)
                        y1 = img.get("bottom", 0)
                        result.append({
                            "name": name,
                            "x": x0 / pw,
                            "y": y0 / ph,
                            "width": (x1 - x0) / pw,
                            "height": (y1 - y0) / ph,
                        })
        except Exception:
            pass
        return result

    @staticmethod
    def _get_images_via_pikepdf(pdf_path: str, page_index: int) -> list[dict]:
        """Parse image XObjects from the content stream using pikepdf.
        Detects images placed as  q [a 0 0 d e f] cm /Name Do Q  blocks."""
        try:
            import pikepdf
            pdf = pikepdf.open(pdf_path)
            try:
                if page_index >= len(pdf.pages):
                    return []
                page = pdf.pages[page_index]
                mb   = page.MediaBox
                pw   = float(mb[2]) - float(mb[0])
                ph   = float(mb[3]) - float(mb[1])
                mb_x = float(mb[0])
                mb_y = float(mb[1])

                # Collect names of image XObjects registered in /Resources
                xobjects = page.Resources.get("/XObject", {})
                image_keys: set[str] = set()
                for k, xobj in xobjects.items():
                    try:
                        if xobj.get("/Subtype") == pikepdf.Name("/Image"):
                            image_keys.add(str(k))   # e.g. "/NewImg1"
                    except Exception:
                        pass

                if not image_keys:
                    return []

                result = []
                instructions = list(pikepdf.parse_content_stream(page))
                i = 0
                while i < len(instructions):
                    ops, op = instructions[i]
                    if op != pikepdf.Operator("q"):
                        i += 1
                        continue
                    # Scan forward for cm / Do / Q inside this q…Q block
                    ctm: list[float] | None = None
                    do_key: str | None = None
                    j = i + 1
                    depth = 1
                    while j < len(instructions) and depth > 0:
                        jops, jop = instructions[j]
                        if jop == pikepdf.Operator("q"):
                            depth += 1
                        elif jop == pikepdf.Operator("Q"):
                            depth -= 1
                        elif jop == pikepdf.Operator("cm") and len(jops) == 6:
                            ctm = [float(x) for x in jops]
                        elif jop == pikepdf.Operator("Do") and jops:
                            key = str(jops[0])   # "/NewImg1"
                            if key in image_keys:
                                do_key = key
                        j += 1

                    if ctm is not None and do_key is not None:
                        # CTM [a 0 0 d e f]: image occupies (e,f)..(e+a, f+d) in PDF space
                        pdf_x = ctm[4] - mb_x
                        pdf_y = ctm[5] - mb_y
                        pdf_w = abs(ctm[0])
                        pdf_h = abs(ctm[3])
                        norm_x = pdf_x / pw
                        norm_y = 1.0 - (pdf_y + pdf_h) / ph  # top-left origin
                        norm_w = pdf_w / pw
                        norm_h = pdf_h / ph
                        result.append({
                            "name": do_key[1:],  # strip leading "/"
                            "x": norm_x,
                            "y": norm_y,
                            "width": norm_w,
                            "height": norm_h,
                        })
                        i = j  # skip to after the Q (image block consumed)
                    else:
                        i += 1  # not an image block — step in normally
                return result
            finally:
                pdf.close()
        except Exception:
            return []

    @staticmethod
    def delete_image(input_path: str, output_path: str, page_index: int, xobj_name: str) -> None:
        """Replace the image XObject with a white rectangle (effectively deletes it visually)."""
        from PIL import Image as PilImage
        import pikepdf

        pdf = pikepdf.open(input_path)
        page = pdf.pages[page_index]
        xobjects = page.Resources.get("/XObject", {})
        key = f"/{xobj_name}"
        if key not in xobjects:
            pdf.close()
            raise KeyError(f"XObject {key} not found on page {page_index}")

        xobj = xobjects[key]
        orig_w = int(xobj.get("/Width", 1))
        orig_h = int(xobj.get("/Height", 1))

        white = PilImage.new("RGB", (orig_w, orig_h), (255, 255, 255))
        img_bytes = white.tobytes()

        new_xobj = pikepdf.Stream(pdf, img_bytes)
        new_xobj["/Type"] = pikepdf.Name("/XObject")
        new_xobj["/Subtype"] = pikepdf.Name("/Image")
        new_xobj["/Width"] = pikepdf.Integer(orig_w)
        new_xobj["/Height"] = pikepdf.Integer(orig_h)
        new_xobj["/ColorSpace"] = pikepdf.Name("/DeviceRGB")
        new_xobj["/BitsPerComponent"] = pikepdf.Integer(8)

        xobjects[key] = new_xobj
        pdf.save(output_path)
        pdf.close()

    @staticmethod
    def replace_image(
        input_path: str, output_path: str,
        page_index: int, xobj_name: str,
        new_image_path: str,
    ) -> None:
        """Replace the image XObject with a new image (resized to original dimensions)."""
        from PIL import Image as PilImage
        import pikepdf

        pdf = pikepdf.open(input_path)
        page = pdf.pages[page_index]
        xobjects = page.Resources.get("/XObject", {})
        key = f"/{xobj_name}"
        if key not in xobjects:
            pdf.close()
            raise KeyError(f"XObject {key} not found on page {page_index}")

        xobj = xobjects[key]
        orig_w = int(xobj.get("/Width", 1))
        orig_h = int(xobj.get("/Height", 1))

        new_img = PilImage.open(new_image_path).convert("RGB")
        new_img = new_img.resize((orig_w, orig_h), PilImage.LANCZOS)
        img_bytes = new_img.tobytes()

        new_xobj = pikepdf.Stream(pdf, img_bytes)
        new_xobj["/Type"] = pikepdf.Name("/XObject")
        new_xobj["/Subtype"] = pikepdf.Name("/Image")
        new_xobj["/Width"] = pikepdf.Integer(orig_w)
        new_xobj["/Height"] = pikepdf.Integer(orig_h)
        new_xobj["/ColorSpace"] = pikepdf.Name("/DeviceRGB")
        new_xobj["/BitsPerComponent"] = pikepdf.Integer(8)

        xobjects[key] = new_xobj
        pdf.save(output_path)
        pdf.close()
