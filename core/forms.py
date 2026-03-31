"""
PDF form field reading and filling via pikepdf.
JSON embedding via XMP metadata (invisible to the user, extractable by N8N).
"""
from __future__ import annotations

import json
from typing import Any, Optional
import pikepdf
from PySide6.QtCore import QRectF


def _pdf_stream_text(text: str) -> str:
    """Encode *text* for use inside a PDF content-stream ``(…) Tj`` operator.

    The font uses WinAnsiEncoding (cp1252).  Characters outside printable ASCII
    (bytes 32-126) — including '€' (cp1252 byte 0x80) — are output as PDF octal
    escapes (e.g. ``\\200``).  PDF special characters ``\\``, ``(``, ``)`` are
    escaped regardless of their byte value.  Unknown characters are replaced by ``?``.
    """
    result: list[str] = []
    for byte in text.encode("cp1252", errors="replace"):
        if byte == 0x5C:          # backslash
            result.append("\\\\")
        elif byte == 0x28:        # (
            result.append("\\(")
        elif byte == 0x29:        # )
            result.append("\\)")
        elif 32 <= byte <= 126:   # printable ASCII — output as-is
            result.append(chr(byte))
        else:                     # non-ASCII WinAnsi byte → octal escape
            result.append(f"\\{byte:03o}")
    return "".join(result)


def _pdf_string(text: str) -> pikepdf.String:
    """Return a pikepdf.String correctly encoded for PDF.

    PDF supports two string encodings:
    - PDFDocEncoding  : covers U+0000–U+00FF (roughly Latin-1).
    - UTF-16BE + BOM  : required for any character beyond U+00FF
                        (e.g. € U+20AC, curly quotes, …).

    pikepdf ≥ 3 encodes Python str automatically: Latin-1 characters stay in
    PDFDocEncoding; anything beyond U+00FF is stored as UTF-16BE with BOM.
    Passing raw bytes would create a PDF *byte string* (not a text string) and
    bypass this logic, so we always pass a Python str.

    NOTE: the appearance stream (/AP) is handled separately by _pdf_stream_text
    using WinAnsiEncoding octal escapes, because content-stream Tj operators use
    the font's byte encoding, not PDF text-string encoding.
    """
    return pikepdf.String(text)


# Bit flags (PDF spec, 1-based → value = 2^(bit-1))
_FLAG_RADIO = 1 << 15   # bit 16 — radio button group
_FLAG_COMBO = 1 << 17   # bit 18 — combobox (choice field)


class FormManager:
    """Read and fill PDF AcroForm fields."""

    def __init__(self) -> None:
        self._pdf: Optional[pikepdf.Pdf] = None

    def attach(self, pdf: pikepdf.Pdf) -> None:
        self._pdf = pdf

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def has_form(self) -> bool:
        """True if the PDF contains AcroForm fields."""
        if not self._pdf:
            return False
        try:
            return "/AcroForm" in self._pdf.Root and "/Fields" in self._pdf.Root.AcroForm
        except Exception:
            return False

    def get_fields(self) -> dict[str, Any]:
        """Return {field_name: value} — value is str, bool, or str for dropdowns."""
        if not self._pdf:
            return {}
        result: dict[str, Any] = {}
        try:
            self._collect_fields(self._pdf.Root.AcroForm.Fields, result)
        except (AttributeError, KeyError):
            pass
        return result

    def get_field_definitions(self) -> list[dict]:
        """Return rich field descriptors: name, type, value, options (for radio/dropdown)."""
        if not self._pdf:
            return []
        defs: list[dict] = []
        try:
            self._collect_definitions(self._pdf.Root.AcroForm.Fields, defs)
        except (AttributeError, KeyError):
            pass
        return defs

    def set_field(self, name: str, value: str) -> None:
        """Set a form field value by name (value is always a string)."""
        if not self._pdf:
            return
        try:
            self._set_field_recursive(self._pdf.Root.AcroForm.Fields, name, value)
        except (AttributeError, KeyError):
            pass

    def embed_json(self, values: dict) -> None:
        """Store form values as JSON in the PDF XMP metadata (invisible to the user)."""
        if not self._pdf:
            return
        with self._pdf.open_metadata() as meta:
            meta["pdfeditor:formdata"] = json.dumps(values, ensure_ascii=False)

    def get_embedded_json(self) -> Optional[dict]:
        """Read back the JSON embedded by embed_json(). Returns None if absent."""
        if not self._pdf:
            return None
        try:
            meta = self._pdf.open_metadata()
            raw = meta.get("pdfeditor:formdata")
            if raw:
                return json.loads(raw)
        except Exception:
            pass
        return None

    # ------------------------------------------------------------------
    # Helpers for label color formatting
    # ------------------------------------------------------------------

    @staticmethod
    def _color_to_rg(color_hex: str) -> str:
        """Convert '#RRGGBB' → PDF fill color op  ('r g b rg' or '0 g' for black)."""
        try:
            h = color_hex.lstrip("#")
            if len(h) == 6:
                r = int(h[0:2], 16) / 255.0
                g = int(h[2:4], 16) / 255.0
                b = int(h[4:6], 16) / 255.0
                if r == 0.0 and g == 0.0 and b == 0.0:
                    return "0 g"
                return f"{r:.4f} {g:.4f} {b:.4f} rg"
        except Exception:
            pass
        return "0 g"

    @staticmethod
    def _color_to_RG(color_hex: str) -> str:
        """Convert '#RRGGBB' → PDF stroke color op ('r g b RG' or '0 G' for black)."""
        try:
            h = color_hex.lstrip("#")
            if len(h) == 6:
                r = int(h[0:2], 16) / 255.0
                g = int(h[2:4], 16) / 255.0
                b = int(h[4:6], 16) / 255.0
                if r == 0.0 and g == 0.0 and b == 0.0:
                    return "0 G"
                return f"{r:.4f} {g:.4f} {b:.4f} RG"
        except Exception:
            pass
        return "0 G"

    def add_field(
        self,
        name: str,
        ftype: str,          # "text" | "checkbox" | "dropdown" | "radio" | "label"
        norm_rect: QRectF,   # normalized coords (0-1) on the page
        page_idx: int,
        options: Optional[list[str]] = None,
        *,
        font_size: Optional[float] = None,   # label/texte: explicit pt size
        bold: bool = False,                   # label/texte
        italic: bool = False,                 # label/texte
        color: str = "#000000",              # label/texte: text color
        underline: bool = False,             # label/texte
        letter_spacing: float = 0.0,         # label/texte: extra Tc spacing in pt
        opacity: float = 1.0,               # texte: annotation opacity 0.0-1.0
        bg_white: bool = False,             # texte: white background in AP stream
        no_wrap: bool = False,              # texte: fit on one line (auto-shrink font)
        bg_color: str = "",                 # texte/label: explicit background color (hex or "")
        is_ocr: bool = False,               # texte: OCR overlay — hide /T, add PDFOCR marker
    ) -> None:
        """Create a new AcroForm field at the given normalized position."""
        if not self._pdf:
            return
        acroform = self._ensure_acroform()
        page = self._pdf.pages[page_idx]
        mb = page.get("/MediaBox", pikepdf.Array([0, 0, 595, 842]))
        pw = float(mb[2]) - float(mb[0])
        ph = float(mb[3]) - float(mb[1])

        # Normalized → PDF coords (flip Y axis: PDF origin is bottom-left)
        x0 = norm_rect.x() * pw
        y1 = (1.0 - norm_rect.y()) * ph
        x1 = (norm_rect.x() + norm_rect.width()) * pw
        y0 = (1.0 - norm_rect.y() - norm_rect.height()) * ph
        pdf_rect = [x0, y0, x1, y1]
        DA = pikepdf.String("/Helv 12 Tf 0 g")

        if ftype == "text":
            field = self._pdf.make_indirect(pikepdf.Dictionary(
                Type=pikepdf.Name.Annot, Subtype=pikepdf.Name.Widget,
                FT=pikepdf.Name.Tx, T=pikepdf.String(name),
                Rect=pikepdf.Array(pdf_rect),
                V=pikepdf.String(""), DA=DA,
                MK=pikepdf.Dictionary(BC=pikepdf.Array([0, 0, 0])),
            ))
            self._add_to_page_annots(page, field)
            acroform["/Fields"].append(field)

        elif ftype == "checkbox":
            opts = options or []
            if not opts:
                # Single nameless checkbox
                field = self._pdf.make_indirect(pikepdf.Dictionary(
                    Type=pikepdf.Name.Annot, Subtype=pikepdf.Name.Widget,
                    FT=pikepdf.Name.Btn, T=pikepdf.String(name),
                    Rect=pikepdf.Array(pdf_rect),
                    V=pikepdf.Name.Off, AS=pikepdf.Name.Off, DA=DA,
                ))
                self._add_to_page_annots(page, field)
                acroform["/Fields"].append(field)
            else:
                # One independent checkbox per option, spread horizontally
                n = len(opts)
                slot_w = (x1 - x0) / n
                for i, opt in enumerate(opts):
                    kx0 = x0 + i * slot_w
                    kx1 = kx0 + slot_w * 0.85
                    cname = f"{name}_{opt}" if opt else f"{name}_{i}"
                    field = self._pdf.make_indirect(pikepdf.Dictionary(
                        Type=pikepdf.Name.Annot, Subtype=pikepdf.Name.Widget,
                        FT=pikepdf.Name.Btn, T=pikepdf.String(cname),
                        TU=pikepdf.String(opt),
                        PDFG=pikepdf.String(name),   # group base name
                        Rect=pikepdf.Array([kx0, y0, kx1, y1]),
                        V=pikepdf.Name.Off, AS=pikepdf.Name.Off, DA=DA,
                    ))
                    self._add_to_page_annots(page, field)
                    acroform["/Fields"].append(field)

        elif ftype == "dropdown":
            opts = options or []
            field = self._pdf.make_indirect(pikepdf.Dictionary(
                Type=pikepdf.Name.Annot, Subtype=pikepdf.Name.Widget,
                FT=pikepdf.Name.Ch, Ff=pikepdf.Integer(131072),
                T=pikepdf.String(name),
                Rect=pikepdf.Array(pdf_rect),
                Opt=pikepdf.Array([pikepdf.String(o) for o in opts]),
                V=pikepdf.String(""), DA=DA,
                MK=pikepdf.Dictionary(BC=pikepdf.Array([0, 0, 0])),
            ))
            self._add_to_page_annots(page, field)
            acroform["/Fields"].append(field)

        elif ftype == "radio":
            opts = options or []
            parent = self._pdf.make_indirect(pikepdf.Dictionary(
                FT=pikepdf.Name.Btn, Ff=pikepdf.Integer(32768),
                T=pikepdf.String(name), V=pikepdf.Name.Off, DA=DA,
            ))
            n = len(opts) or 1
            slot_w = (x1 - x0) / n
            kids = []
            for i, opt in enumerate(opts):
                kx0 = x0 + i * slot_w
                kx1 = kx0 + slot_w * 0.85
                kid = self._pdf.make_indirect(pikepdf.Dictionary(
                    Type=pikepdf.Name.Annot, Subtype=pikepdf.Name.Widget,
                    Parent=parent,
                    Rect=pikepdf.Array([kx0, y0, kx1, y1]),
                    AS=pikepdf.Name.Off,
                    TU=pikepdf.String(opt),  # tooltip = option name (fallback for _radio_options)
                ))
                kids.append(kid)
                self._add_to_page_annots(page, kid)
            parent["/Kids"] = pikepdf.Array(kids)
            acroform["/Fields"].append(parent)

        elif ftype == "texte":
            # Bloc de texte multi-ligne — FreeText annotation avec AP stream multi-ligne.
            text = options[0] if options is not None and len(options) > 0 else name
            lines = text.split("\n") if text else [""]
            fs = int(font_size) if font_size is not None else max(8, int((y1 - y0) * 0.10))
            fs = max(6, fs)
            w = x1 - x0
            h = y1 - y0

            # Use full standard PDF font names so renderers (pdfium etc.) resolve them
            # reliably without needing a custom alias in the resource dictionary.
            _variant_map = {
                (False, False): ("Helvetica",             "Helvetica"),
                (True,  False): ("Helvetica-Bold",        "Helvetica-Bold"),
                (False, True):  ("Helvetica-Oblique",     "Helvetica-Oblique"),
                (True,  True):  ("Helvetica-BoldOblique", "Helvetica-BoldOblique"),
            }
            font_key, base_font_name = _variant_map[(bold, italic)]
            dr_fonts = acroform["/DR"]["/Font"]
            if f"/{font_key}" not in dr_fonts:
                dr_fonts[f"/{font_key}"] = self._pdf.make_indirect(pikepdf.Dictionary(
                    Type=pikepdf.Name.Font, Subtype=pikepdf.Name.Type1,
                    BaseFont=pikepdf.Name("/" + base_font_name),
                    Encoding=pikepdf.Name.WinAnsiEncoding,
                ))
            font_ref = dr_fonts[f"/{font_key}"]
            if "/Resources" not in page:
                page["/Resources"] = pikepdf.Dictionary()
            res = page["/Resources"]
            if "/Font" not in res:
                res["/Font"] = pikepdf.Dictionary()
            if f"/{font_key}" not in res["/Font"]:
                res["/Font"][f"/{font_key}"] = font_ref

            color_rg = self._color_to_rg(color)
            color_RG = self._color_to_RG(color)
            line_h = fs * 1.4
            # Baseline near the top; guard against h ≈ fs (pdfplumber tight bbox).
            start_y = max(h - fs - 2, round(fs * 0.28))
            # Helvetica avg char width ≈ 0.55 × fs; leave 4pt margin
            char_w = fs * 0.55
            max_line_w = max(char_w, w - 4.0)

            # Word-wrap or no-wrap (single line with auto-fit font)
            wrapped: list[str] = []
            if no_wrap:
                # Single line: shrink font until text fits width
                single = " ".join(lines)
                # Use 0.48 (Helvetica avg char width) instead of 0.55 to avoid
                # over-shrinking — the box is already sized for the font.
                while fs > 4 and len(single) * (fs * 0.48) > max_line_w:
                    fs -= 1
                char_w = fs * 0.48
                line_h = fs * 1.4
                # Place baseline so descenders (≈22% of fs below baseline) stay inside
                # the box. h - fs - 2 breaks when h ≈ fs (gives negative start_y).
                start_y = max(round(fs * 0.28), 2)
                wrapped = [single]
            else:
                for paragraph in lines:
                    words = paragraph.split(" ")
                    cur = ""
                    for word in words:
                        candidate = (cur + " " + word).strip() if cur else word
                        if len(candidate) * char_w <= max_line_w:
                            cur = candidate
                        else:
                            if cur:
                                wrapped.append(cur)
                            # If a single word is wider than the box, keep it as-is
                            cur = word
                    if cur:
                        wrapped.append(cur)
            if not wrapped:
                wrapped = [""]

            _safe = _pdf_stream_text

            tc_line = f"{letter_spacing:.4f} Tc\n" if letter_spacing > 0.0 else ""

            _bg = bg_color if bg_color else ("#ffffff" if bg_white else "")
            if _bg:
                _r, _g, _b = (int(_bg.lstrip("#")[i:i+2], 16) / 255 for i in (0, 2, 4))
                bg_rect = f"q\n{_r:.4f} {_g:.4f} {_b:.4f} rg\n0 0 {w:.2f} {h:.2f} re\nf\nQ\n"
            else:
                bg_rect = ""
            parts = [bg_rect, "q\nBT\n", f"/{font_key} {fs} Tf\n", f"{color_rg}\n", tc_line]
            line_baselines: list[float] = []
            for i, line in enumerate(wrapped):
                if i == 0:
                    parts.append(f"2 {start_y:.2f} Td\n")
                    line_baselines.append(start_y)
                else:
                    parts.append(f"0 {-line_h:.2f} Td\n")
                    line_baselines.append(line_baselines[-1] - line_h)
                parts.append(f"({_safe(line)}) Tj\n")
            parts.append("ET\n")

            # Draw underlines outside BT/ET — one per wrapped line
            if underline:
                parts.append(f"{color_RG}\n0.5 w\n")
                for line, baseline in zip(wrapped, line_baselines):
                    text_w = min(w - 4.0, max(4.0, len(line) * char_w))
                    underline_y = baseline - fs * 0.12
                    parts.append(
                        f"2 {underline_y:.2f} m\n"
                        f"{2 + text_w:.2f} {underline_y:.2f} l\nS\n"
                    )

            parts.append("Q\n")

            ap_content = "".join(parts).encode("ascii")
            ap_stream = self._pdf.make_stream(
                ap_content,
                pikepdf.Dictionary(
                    Type=pikepdf.Name.XObject,
                    Subtype=pikepdf.Name.Form,
                    BBox=pikepdf.Array([0, 0, w, h]),
                    Resources=pikepdf.Dictionary(
                        Font=pikepdf.Dictionary({f"/{font_key}": font_ref})
                    ),
                ),
            )
            self._remove_label_annotation(page, name)
            da_str = f"/{font_key} {fs} Tf {color_rg}"
            annot_dict = pikepdf.Dictionary(
                Type=pikepdf.Name.Annot,
                Subtype=pikepdf.Name.FreeText,
                T=pikepdf.String("" if is_ocr else name),
                Rect=pikepdf.Array(pdf_rect),
                Contents=_pdf_string(text),
                DA=pikepdf.String(da_str),
                BS=pikepdf.Dictionary(W=pikepdf.Integer(0)),
                IC=pikepdf.Array([int(bg_color.lstrip("#")[i:i+2], 16) / 255 for i in (0, 2, 4)]) if bg_color else (pikepdf.Array([1, 1, 1]) if bg_white else pikepdf.Array([])),
                F=pikepdf.Integer(4),
                AP=pikepdf.Dictionary(N=self._pdf.make_indirect(ap_stream)),
                PDUL=pikepdf.Boolean(underline),
                PDLS=pikepdf.Real(letter_spacing),
                PDFT=pikepdf.String("texte"),
                CA=pikepdf.Real(max(0.0, min(1.0, opacity))),
                PDFBG=pikepdf.String(bg_color),
                PDFBGW=pikepdf.Boolean(bg_white),
            )
            if is_ocr:
                annot_dict["/PDFOCR"] = pikepdf.Boolean(True)
                annot_dict["/PDFI"] = pikepdf.String(name)
            annot = self._pdf.make_indirect(annot_dict)
            self._add_to_page_annots(page, annot)
            return

        elif ftype == "image":
            # Embed image directly in the page content stream.
            import io as _io
            import PIL.Image
            image_path = options[0] if options else ""
            if not image_path:
                return
            img = PIL.Image.open(image_path).convert("RGB")
            jpeg_buf = _io.BytesIO()
            img.save(jpeg_buf, format="JPEG", quality=90)
            jpeg_data = jpeg_buf.getvalue()

            # Unique XObject name derived from field identifier
            img_res_name = f"PDFEImg{abs(hash(name)) % 65536:04X}"
            img_xobj = self._pdf.make_stream(
                jpeg_data,
                pikepdf.Dictionary(
                    Type=pikepdf.Name.XObject,
                    Subtype=pikepdf.Name.Image,
                    Width=pikepdf.Integer(img.size[0]),
                    Height=pikepdf.Integer(img.size[1]),
                    ColorSpace=pikepdf.Name.DeviceRGB,
                    BitsPerComponent=pikepdf.Integer(8),
                    Filter=pikepdf.Name.DCTDecode,
                ),
            )
            if "/Resources" not in page:
                page["/Resources"] = pikepdf.Dictionary()
            res = page["/Resources"]
            if "/XObject" not in res:
                res["/XObject"] = pikepdf.Dictionary()
            res["/XObject"][f"/{img_res_name}"] = self._pdf.make_indirect(img_xobj)

            w = x1 - x0
            h = y1 - y0
            draw_cmd = (
                f"q {w:.4f} 0 0 {h:.4f} {x0:.4f} {y0:.4f} cm /{img_res_name} Do Q\n"
            )
            new_stream = self._pdf.make_indirect(
                self._pdf.make_stream(draw_cmd.encode("latin-1"))
            )
            contents = page.get("/Contents")
            if contents is None:
                page["/Contents"] = new_stream
            elif isinstance(contents, pikepdf.Array):
                page["/Contents"].append(new_stream)
            else:
                page["/Contents"] = pikepdf.Array([contents, new_stream])
            return

        elif ftype == "label":
            # FreeText annotation — natively editable, movable, deletable.
            # /T stores the identifier so the annotation can be replaced on re-draw.
            text = (options[0] if options else name)
            fs = int(font_size) if font_size is not None else max(8, int((y1 - y0) * 0.65))
            fs = max(6, fs)
            w = x1 - x0
            h = y1 - y0
            baseline = h * 0.25   # baseline offset inside the bounding box

            # Use full standard PDF font names so renderers resolve them reliably
            _variant_map = {
                (False, False): ("Helvetica",             "Helvetica"),
                (True,  False): ("Helvetica-Bold",        "Helvetica-Bold"),
                (False, True):  ("Helvetica-Oblique",     "Helvetica-Oblique"),
                (True,  True):  ("Helvetica-BoldOblique", "Helvetica-BoldOblique"),
            }
            font_key, base_font_name = _variant_map[(bold, italic)]

            # Ensure the chosen font variant is in the AcroForm DR and page resources
            dr_fonts = acroform["/DR"]["/Font"]
            if f"/{font_key}" not in dr_fonts:
                dr_fonts[f"/{font_key}"] = self._pdf.make_indirect(pikepdf.Dictionary(
                    Type=pikepdf.Name.Font,
                    Subtype=pikepdf.Name.Type1,
                    BaseFont=pikepdf.Name("/" + base_font_name),
                    Encoding=pikepdf.Name.WinAnsiEncoding,
                ))
            font_ref = dr_fonts[f"/{font_key}"]
            if "/Resources" not in page:
                page["/Resources"] = pikepdf.Dictionary()
            res = page["/Resources"]
            if "/Font" not in res:
                res["/Font"] = pikepdf.Dictionary()
            if f"/{font_key}" not in res["/Font"]:
                res["/Font"][f"/{font_key}"] = font_ref

            color_rg = self._color_to_rg(color)
            color_RG = self._color_to_RG(color)
            tc_line = f"{letter_spacing:.4f} Tc\n" if letter_spacing > 0.0 else ""

            # Encode text for the appearance stream (WinAnsiEncoding, octal escapes)
            safe = _pdf_stream_text(text)

            # Approximate text width (Helvetica avg ~0.55 × fs per char)
            text_w = min(w - 4.0, max(4.0, len(text) * fs * 0.55))
            underline_y = baseline - fs * 0.12   # slightly below baseline

            # Build explicit appearance stream (transparent background)
            # color_rg (fill) is set inside BT so pdfium applies it to text rendering
            _bg = bg_color
            if _bg:
                _r2, _g2, _b2 = (int(_bg.lstrip("#")[i:i+2], 16) / 255 for i in (0, 2, 4))
                bg_rect2 = f"q\n{_r2:.4f} {_g2:.4f} {_b2:.4f} rg\n0 0 {w:.2f} {h:.2f} re\nf\nQ\n"
            else:
                bg_rect2 = ""
            parts = [
                bg_rect2,
                "q\n",
                "BT\n",
                f"/{font_key} {fs} Tf\n",
                f"{color_rg}\n",
                tc_line,
                f"2 {baseline:.2f} Td\n",
                f"({safe}) Tj\n",
                "ET\n",
            ]
            if underline:
                parts += [
                    f"{color_RG}\n",
                    f"0.5 w\n",
                    f"2 {underline_y:.2f} m\n",
                    f"{2 + text_w:.2f} {underline_y:.2f} l\n",
                    "S\n",
                ]
            parts.append("Q\n")

            ap_content = "".join(parts).encode("ascii")
            ap_stream = self._pdf.make_stream(
                ap_content,
                pikepdf.Dictionary(
                    Type=pikepdf.Name.XObject,
                    Subtype=pikepdf.Name.Form,
                    BBox=pikepdf.Array([0, 0, w, h]),
                    Resources=pikepdf.Dictionary(
                        Font=pikepdf.Dictionary({f"/{font_key}": font_ref})
                    ),
                ),
            )

            # Remove any existing label annotation with the same identifier
            self._remove_label_annotation(page, name)

            da_str = f"/{font_key} {fs} Tf {color_rg}"
            annot = self._pdf.make_indirect(pikepdf.Dictionary(
                Type=pikepdf.Name.Annot,
                Subtype=pikepdf.Name.FreeText,
                T=pikepdf.String(name),          # identifier for future replacement
                Rect=pikepdf.Array(pdf_rect),
                Contents=_pdf_string(text),
                DA=pikepdf.String(da_str),
                BS=pikepdf.Dictionary(W=pikepdf.Integer(0)),  # no border
                IC=pikepdf.Array([int(bg_color.lstrip("#")[i:i+2], 16)/255 for i in (0,2,4)]) if bg_color else pikepdf.Array([]),
                F=pikepdf.Integer(4),            # Print flag
                AP=pikepdf.Dictionary(N=self._pdf.make_indirect(ap_stream)),
                # Custom keys (PDF-Editor private): survive save/reload
                PDUL=pikepdf.Boolean(underline),
                PDLS=pikepdf.Real(letter_spacing),
                PDFT=pikepdf.String("label"),
                PDFBG=pikepdf.String(bg_color),
            ))
            self._add_to_page_annots(page, annot)
            return  # no AcroForm update needed for labels

        acroform["/NeedAppearances"] = pikepdf.Boolean(True)

    def get_form_overlays_for_page(self, page_idx: int) -> list[dict]:
        """Return overlay descriptors {name, type, nx, ny, nw, nh} for page_idx."""
        if not self._pdf:
            return []
        result = []
        try:
            page = self._pdf.pages[page_idx]
            if "/Annots" not in page:
                return []
            mb = page.get("/MediaBox", pikepdf.Array([0, 0, 595, 842]))
            pw = float(mb[2]) - float(mb[0])
            ph = float(mb[3]) - float(mb[1])

            for annot in page["/Annots"]:
                if str(annot.get("/Subtype", "")) != "/Widget":
                    continue
                rect = annot.get("/Rect")
                if not rect:
                    continue
                x0, y0, x1, y1 = [float(r) for r in rect]
                name = str(annot.get("/T", ""))
                ft = str(annot.get("/FT", ""))
                if not name and "/Parent" in annot:
                    name = str(annot["/Parent"].get("/T", ""))
                    ft = ft or str(annot["/Parent"].get("/FT", ""))
                ftype = {"Tx": "text", "Btn": "checkbox", "Ch": "dropdown"}.get(
                    ft.lstrip("/"), "field"
                )
                ff = int(annot.get("/Ff", 0))
                if not ff and "/Parent" in annot:
                    ff = int(annot["/Parent"].get("/Ff", 0))
                if ftype == "checkbox" and (ff & _FLAG_RADIO):
                    ftype = "radio"
                result.append({
                    "name": name, "type": ftype,
                    "nx": x0 / pw,
                    "ny": 1.0 - y1 / ph,
                    "nw": (x1 - x0) / pw,
                    "nh": (y1 - y0) / ph,
                })
        except Exception:
            pass
        return result

    def flatten(self) -> None:
        """Flatten the form (make fields non-editable)."""
        if not self._pdf:
            return
        for page in self._pdf.pages:
            if "/Annots" in page:
                page["/Annots"] = pikepdf.Array([
                    a for a in page["/Annots"]
                    if str(a.get("/Subtype", "")) != "/Widget"
                ])
        if "/AcroForm" in self._pdf.Root:
            del self._pdf.Root["/AcroForm"]

    # ------------------------------------------------------------------
    # Internal — field traversal
    # ------------------------------------------------------------------

    def _collect_fields(self, fields_array: pikepdf.Array, result: dict) -> None:
        for field in fields_array:
            name = str(field.get("/T", ""))
            ft   = str(field.get("/FT", ""))
            ff   = int(field.get("/Ff", 0))

            if "/Kids" in field and not (ft == "/Btn" and (ff & _FLAG_RADIO)):
                # Hierarchical group — recurse (not radio kids)
                self._collect_fields(field["/Kids"], result)
                continue

            if not name:
                continue

            v = field.get("/V", "")
            if ft == "/Btn":
                if ff & _FLAG_RADIO:
                    # Radio: parent /V holds selected option name
                    raw = str(v).lstrip("/")
                    result[name] = raw if raw != "Off" else ""
                else:
                    # Checkbox: compare /AS to /Yes
                    as_val = str(field.get("/AS", v))
                    result[name] = as_val in ("/Yes", "Yes")
            else:
                result[name] = str(v).lstrip("/")

    def _collect_definitions(self, fields_array: pikepdf.Array, defs: list) -> None:
        for field in fields_array:
            name = str(field.get("/T", ""))
            ft   = str(field.get("/FT", ""))
            ff   = int(field.get("/Ff", 0))

            if "/Kids" in field and not (ft == "/Btn" and (ff & _FLAG_RADIO)):
                self._collect_definitions(field["/Kids"], defs)
                continue

            if not name:
                continue

            v = field.get("/V", "")

            if ft == "/Tx":
                defs.append({"name": name, "type": "text", "value": str(v)})

            elif ft == "/Btn":
                if ff & _FLAG_RADIO:
                    raw = str(v).lstrip("/")
                    options = self._radio_options(field)
                    defs.append({
                        "name": name, "type": "radio",
                        "value": raw if raw != "Off" else "",
                        "options": options,
                    })
                else:
                    as_val = str(field.get("/AS", v))
                    group  = str(field.get("/PDFG", "")).strip()
                    option = str(field.get("/TU",   "")).strip()
                    defs.append({
                        "name":   name,
                        "type":   "checkbox",
                        "value":  as_val in ("/Yes", "Yes"),
                        "group":  group,
                        "option": option,
                    })

            elif ft == "/Ch":
                opts = self._choice_options(field)
                defs.append({
                    "name": name,
                    "type": "dropdown" if (ff & _FLAG_COMBO) else "list",
                    "value": str(v),
                    "options": opts,
                })

    def _radio_options(self, radio_parent) -> list[str]:
        """Extract option names from radio kids' AP streams, or TU tooltip as fallback."""
        options: list[str] = []
        try:
            for kid in radio_parent["/Kids"]:
                found = False
                try:
                    for key in kid["/AP"]["/N"].keys():
                        opt = str(key).lstrip("/")
                        if opt != "Off" and opt not in options:
                            options.append(opt)
                            found = True
                except Exception:
                    pass
                if not found:
                    tu = str(kid.get("/TU", "")).strip()
                    if tu and tu not in options:
                        options.append(tu)
        except Exception:
            pass
        return options

    def _choice_options(self, field) -> list[str]:
        opts_raw = field.get("/Opt", [])
        result = []
        for opt in opts_raw:
            if isinstance(opt, pikepdf.Array):
                result.append(str(opt[1]))   # (export_val, display_val)
            else:
                result.append(str(opt))
        return result

    # ------------------------------------------------------------------
    # Internal — set field value
    # ------------------------------------------------------------------

    def _set_field_recursive(
        self, fields_array: pikepdf.Array, name: str, value: str
    ) -> bool:
        for field in fields_array:
            ft = str(field.get("/FT", ""))
            ff = int(field.get("/Ff", 0))
            is_radio = ft == "/Btn" and bool(ff & _FLAG_RADIO)

            if "/Kids" in field and not is_radio:
                if self._set_field_recursive(field["/Kids"], name, value):
                    return True

            field_name = str(field.get("/T", ""))
            if field_name != name:
                continue

            if ft == "/Btn":
                if is_radio:
                    self._set_radio(field, value)
                else:
                    state = pikepdf.Name("/Yes" if value.lower() in ("true", "yes", "1") else "/Off")
                    field["/V"]  = state
                    field["/AS"] = state
            else:
                field["/V"] = pikepdf.String(value)
            return True
        return False

    def _set_radio(self, parent, option_name: str) -> None:
        """Set radio group: update parent /V and each kid's /AS."""
        parent["/V"] = pikepdf.Name(f"/{option_name}")
        try:
            for kid in parent["/Kids"]:
                # Determine which option this kid represents
                kid_opts = []
                try:
                    for key in kid["/AP"]["/N"].keys():
                        opt = str(key).lstrip("/")
                        if opt != "Off":
                            kid_opts.append(opt)
                except Exception:
                    pass
                kid["/AS"] = (
                    pikepdf.Name(f"/{option_name}")
                    if option_name in kid_opts
                    else pikepdf.Name.Off
                )
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Internal — AcroForm initialisation / page annotations
    # ------------------------------------------------------------------

    def get_all_labels_for_page(self, page_idx: int) -> list[dict]:
        """Return [{name, text, nx, ny, nw, nh, kind='label'}] for all FreeText labels on the page."""
        if not self._pdf:
            return []
        result = []
        try:
            page = self._pdf.pages[page_idx]
            if "/Annots" not in page:
                return []
            mb = page.get("/MediaBox", pikepdf.Array([0, 0, 595, 842]))
            pw = float(mb[2]) - float(mb[0])
            ph = float(mb[3]) - float(mb[1])
            for annot in page["/Annots"]:
                if str(annot.get("/Subtype", "")) != "/FreeText":
                    continue
                name = str(annot.get("/T", ""))
                is_ocr_ann = bool(annot.get("/PDFOCR", False))
                if not name:
                    if is_ocr_ann:
                        name = str(annot.get("/PDFI", ""))
                    if not name:
                        continue
                rect = annot.get("/Rect")
                if not rect:
                    continue
                x0, y0, x1, y1 = [float(v) for v in rect]
                result.append({
                    "kind": "label",
                    "ftype": str(annot.get("/PDFT", "label")).strip(),
                    "name": name,
                    "text": str(annot.get("/Contents", "")),
                    "nx": x0 / pw,
                    "ny": 1.0 - y1 / ph,
                    "nw": (x1 - x0) / pw,
                    "nh": (y1 - y0) / ph,
                    "is_ocr": is_ocr_ann,
                })
        except Exception:
            pass
        return result

    def field_name_exists(self, name: str) -> bool:
        """Return True if name is already used by an AcroForm field or a FreeText label."""
        if not self._pdf:
            return False
        # Check AcroForm fields
        if name in self.get_fields():
            return True
        # Check FreeText labels across all pages
        for i in range(len(self._pdf.pages)):
            for lbl in self.get_all_labels_for_page(i):
                if lbl["name"] == name:
                    return True
        return False

    def move_field(self, page_idx: int, name: str,
                   new_nx: float, new_ny: float, nw: float, nh: float) -> None:
        """Move a Widget field annotation to a new normalized position."""
        if not self._pdf:
            return
        try:
            page = self._pdf.pages[page_idx]
            mb = page.get("/MediaBox", pikepdf.Array([0, 0, 595, 842]))
            pw = float(mb[2]) - float(mb[0])
            ph = float(mb[3]) - float(mb[1])
            x0 = new_nx * pw
            y1 = (1.0 - new_ny) * ph
            x1 = (new_nx + nw) * pw
            y0 = (1.0 - new_ny - nh) * ph
            new_rect = [x0, y0, x1, y1]
            if "/Annots" not in page:
                return
            for annot in page["/Annots"]:
                if str(annot.get("/Subtype", "")) != "/Widget":
                    continue
                t = str(annot.get("/T", ""))
                parent_t = ""
                if "/Parent" in annot:
                    parent_t = str(annot["/Parent"].get("/T", ""))
                if t == name or parent_t == name:
                    annot["/Rect"] = pikepdf.Array(new_rect)
        except Exception:
            pass

    def get_label_at(self, page_idx: int, nx: float, ny: float) -> Optional[dict]:
        """Return {name, text, font_size, nx, ny, nw, nh} for a FreeText label under (nx,ny), or None."""
        if not self._pdf:
            return None
        try:
            page = self._pdf.pages[page_idx]
            if "/Annots" not in page:
                return None
            mb = page.get("/MediaBox", pikepdf.Array([0, 0, 595, 842]))
            pw = float(mb[2]) - float(mb[0])
            ph = float(mb[3]) - float(mb[1])
            for annot in page["/Annots"]:
                subtype = str(annot.get("/Subtype", ""))
                t = str(annot.get("/T", ""))
                if subtype != "/FreeText":
                    continue
                # OCR annotations have /T="" — their name is in /PDFI
                is_ocr = bool(annot.get("/PDFOCR", False))
                name = t if t else (str(annot.get("/PDFI", "")) if is_ocr else "")
                if not name:
                    continue
                rect = annot.get("/Rect")
                if not rect:
                    continue
                x0, y0, x1, y1 = [float(v) for v in rect]
                lnx = x0 / pw
                lny = 1.0 - y1 / ph
                lnw = (x1 - x0) / pw
                lnh = (y1 - y0) / ph
                if lnx <= nx <= lnx + lnw and lny <= ny <= lny + lnh:
                    # Parse font size from DA string e.g. "/Helv 14 Tf 0 g"
                    da = str(annot.get("/DA", ""))
                    font_size = 12.0
                    parts = da.split()
                    for i, part in enumerate(parts):
                        if part == "Tf" and i >= 1:
                            try:
                                font_size = float(parts[i - 1])
                            except ValueError:
                                pass
                            break
                    pdft = str(annot.get("/PDFT", "label")).strip()
                    return {
                        "name": name,
                        "ftype": pdft,   # "label" or "texte"
                        "text": str(annot.get("/Contents", "")),
                        "font_size": font_size,
                        "nx": lnx, "ny": lny, "nw": lnw, "nh": lnh,
                        "is_ocr": is_ocr,
                    }
        except Exception:
            pass
        return None

    def get_label_formatting(self, page_idx: int, name: str) -> dict:
        """Return {font_size, bold, italic, color} parsed from the DA of the named FreeText label."""
        default = {"font_size": 12.0, "bold": False, "italic": False, "color": "#000000", "bg_color": ""}
        if not self._pdf:
            return default
        try:
            page = self._pdf.pages[page_idx]
            if "/Annots" not in page:
                return default
            for annot in page["/Annots"]:
                if str(annot.get("/Subtype", "")) != "/FreeText":
                    continue
                ann_name = str(annot.get("/T", "")) or str(annot.get("/PDFI", ""))
                if ann_name != name:
                    continue
                da = str(annot.get("/DA", ""))
                parts = da.split()
                font_key = "Helv"
                font_size = 12.0
                color = "#000000"
                for i, p in enumerate(parts):
                    if p == "Tf" and i >= 1:
                        try:
                            font_size = float(parts[i - 1])
                        except ValueError:
                            pass
                        if i >= 2:
                            font_key = parts[i - 2].lstrip("/")
                        break
                # Parse color: "r g b rg" after Tf, or "g g" (grayscale)
                try:
                    tf_idx = parts.index("Tf")
                    after = parts[tf_idx + 1:]
                    if len(after) >= 4 and after[3] == "rg":
                        r = int(float(after[0]) * 255)
                        g = int(float(after[1]) * 255)
                        b = int(float(after[2]) * 255)
                        color = f"#{r:02x}{g:02x}{b:02x}"
                    elif len(after) >= 2 and after[1] == "g":
                        v = int(float(after[0]) * 255)
                        color = f"#{v:02x}{v:02x}{v:02x}"
                except Exception:
                    pass
                underline_val = bool(annot.get("/PDUL", False))
                spacing_val = float(annot.get("/PDLS", 0.0))
                return {
                    "font_size": font_size,
                    "bold": "Bold" in font_key,
                    "italic": "Oblique" in font_key or "Obl" in font_key,
                    "color": color,
                    "underline": underline_val,
                    "letter_spacing": spacing_val,
                    "bg_color": str(annot.get("/PDFBG", "")),
                    "bg_white": bool(annot.get("/PDFBGW", False)),
                }
        except Exception:
            pass
        return default

    def remove_field(self, name: str) -> None:
        """Remove an AcroForm field (text, checkbox, radio, dropdown) by name.

        Removes matching Widget annotations from every page and the entry from
        AcroForm /Fields (handles both flat and parent/kids structures).
        """
        if not self._pdf:
            return
        try:
            # Remove Widget annotations from all pages
            for page in self._pdf.pages:
                if "/Annots" not in page:
                    continue
                keep = []
                for annot in page["/Annots"]:
                    if str(annot.get("/Subtype", "")) != "/Widget":
                        keep.append(annot)
                        continue
                    annot_name = str(annot.get("/T", ""))
                    parent_name = ""
                    if "/Parent" in annot:
                        parent_name = str(annot["/Parent"].get("/T", ""))
                    if annot_name == name or parent_name == name:
                        continue  # drop this widget
                    keep.append(annot)
                page["/Annots"] = pikepdf.Array(keep)

            # Remove the field entry from AcroForm /Fields
            if "/AcroForm" not in self._pdf.Root:
                return
            fields = self._pdf.Root.AcroForm.get("/Fields", pikepdf.Array())
            self._pdf.Root.AcroForm["/Fields"] = pikepdf.Array([
                f for f in fields
                if str(f.get("/T", "")) != name
            ])
        except Exception:
            pass

    def has_ocr_annotations(self, page_idx: int) -> bool:
        """Return True if the page has at least one OCR overlay annotation (/PDFOCR=True)."""
        if not self._pdf:
            return False
        try:
            page = self._pdf.pages[page_idx]
            if "/Annots" not in page:
                return False
            return any(bool(a.get("/PDFOCR", False)) for a in page["/Annots"])
        except Exception:
            return False

    def remove_ocr_annotations(self, page_idx: int) -> None:
        """Remove all OCR overlay annotations (marked with /PDFOCR) from a page."""
        if not self._pdf:
            return
        try:
            page = self._pdf.pages[page_idx]
            if "/Annots" not in page:
                return
            page["/Annots"] = pikepdf.Array([
                a for a in page["/Annots"]
                if not bool(a.get("/PDFOCR", False))
            ])
        except Exception:
            pass

    def remove_checkbox_group(self, group_name: str) -> None:
        """Remove all checkbox widgets that belong to the given group (PDFG == group_name)."""
        if not self._pdf:
            return
        try:
            for page in self._pdf.pages:
                if "/Annots" not in page:
                    continue
                keep = []
                for annot in page["/Annots"]:
                    if (str(annot.get("/Subtype", "")) == "/Widget"
                            and str(annot.get("/PDFG", "")).strip() == group_name):
                        continue  # drop
                    keep.append(annot)
                page["/Annots"] = pikepdf.Array(keep)
            if "/AcroForm" not in self._pdf.Root:
                return
            fields = self._pdf.Root.AcroForm.get("/Fields", pikepdf.Array())
            self._pdf.Root.AcroForm["/Fields"] = pikepdf.Array([
                f for f in fields
                if str(f.get("/PDFG", "")).strip() != group_name
            ])
        except Exception:
            pass

    def remove_label(self, page_idx: int, name: str) -> None:
        """Remove a FreeText label/texte annotation by name (public API)."""
        if not self._pdf:
            return
        try:
            page = self._pdf.pages[page_idx]
            self._remove_label_annotation(page, name)
        except Exception:
            pass

    def _remove_label_annotation(self, page, name: str) -> None:
        """Remove any FreeText annotation whose /T matches the label identifier."""
        if "/Annots" not in page:
            return
        page["/Annots"] = pikepdf.Array([
            a for a in page["/Annots"]
            if not (
                str(a.get("/Subtype", "")) == "/FreeText"
                and (str(a.get("/T", "")) == name or str(a.get("/PDFI", "")) == name)
            )
        ])

    def _ensure_acroform(self) -> pikepdf.Object:
        if "/AcroForm" not in self._pdf.Root:
            helv = self._pdf.make_indirect(pikepdf.Dictionary(
                Type=pikepdf.Name.Font,
                Subtype=pikepdf.Name.Type1,
                BaseFont=pikepdf.Name.Helvetica,
                Encoding=pikepdf.Name.WinAnsiEncoding,
            ))
            self._pdf.Root["/AcroForm"] = pikepdf.Dictionary(
                Fields=pikepdf.Array([]),
                NeedAppearances=pikepdf.Boolean(True),
                DR=pikepdf.Dictionary(
                    Font=pikepdf.Dictionary({"/Helv": helv})
                ),
            )
        return self._pdf.Root["/AcroForm"]

    def _add_to_page_annots(self, page: pikepdf.Page, annot: pikepdf.Object) -> None:
        if "/Annots" not in page:
            page["/Annots"] = pikepdf.Array([])
        page["/Annots"].append(annot)
