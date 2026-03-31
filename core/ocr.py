"""
OCR integration via Tesseract + pytesseract.
"""
from __future__ import annotations

import os
import re
import subprocess
from collections import defaultdict
from typing import Optional, Callable

from PySide6.QtGui import QImage

try:
    import pytesseract
    from PIL import Image
    HAS_TESSERACT = True
except ImportError:
    HAS_TESSERACT = False


def _find_tesseract() -> Optional[str]:
    """Try to locate tesseract.exe on Windows via registry, common paths, or PATH."""
    import sys
    if sys.platform != "win32":
        return None  # on Linux/macOS pytesseract finds it via PATH

    # 1. Windows Registry (HKLM and HKCU)
    try:
        import winreg
        for hive in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
            for sub in (
                r"SOFTWARE\Tesseract-OCR",
                r"SOFTWARE\WOW6432Node\Tesseract-OCR",
            ):
                try:
                    with winreg.OpenKey(hive, sub) as key:
                        install_dir, _ = winreg.QueryValueEx(key, "InstallDir")
                        candidate = os.path.join(install_dir, "tesseract.exe")
                        if os.path.isfile(candidate):
                            return candidate
                except (FileNotFoundError, OSError):
                    continue
    except Exception:
        pass

    # 2. Common default installation paths
    common_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Tesseract-OCR\tesseract.exe"),
        os.path.expandvars(r"%APPDATA%\Tesseract-OCR\tesseract.exe"),
    ]
    for p in common_paths:
        if os.path.isfile(p):
            return p

    return None  # fall back to PATH resolution by pytesseract


class OCREngine:
    def __init__(self, tesseract_path: str = "") -> None:
        if HAS_TESSERACT:
            # Explicit path from config takes priority
            if tesseract_path and os.path.isfile(tesseract_path):
                pytesseract.pytesseract.tesseract_cmd = tesseract_path
            else:
                # Auto-detect on Windows
                found = _find_tesseract()
                if found:
                    pytesseract.pytesseract.tesseract_cmd = found
        self._available = self._check_available()

    @property
    def is_available(self) -> bool:
        return self._available

    # Text extraction: auto layout detection
    _TESS_CONFIG = "--oem 3 --psm 3"
    # Overlay / line positioning: sparse text — each independent block keeps its own coords.
    # psm 11 = sparse text (préserve la mise en page).
    # --dpi is added dynamically in run_page_lines() from the caller-supplied dpi parameter.
    #   Without the correct DPI, Tesseract assumes ~70 DPI and rejects tall blobs like "€".
    # Dictionaries disabled: avoids "correcting" +, -, %, €, $, °, etc.
    _TESS_LINES_CONFIG_BASE = (
        "--oem 1 --psm 11 "
        "-c load_system_dawg=0 -c load_freq_dawg=0 -c load_bigram_dawg=0 "
        "-c load_punc_dawg=0 -c load_number_dawg=0"
    )

    def run_page(self, image: QImage, lang: str = "fra+eng") -> str:
        """Run OCR on a QImage and return extracted text."""
        if not self._available:
            raise RuntimeError(
                "Tesseract OCR non disponible. "
                "Veuillez l'installer depuis https://github.com/UB-Mannheim/tesseract/wiki"
            )
        pil_image = self._preprocess(self._qimage_to_pil(image))
        text = pytesseract.image_to_string(pil_image, lang=lang, config=self._TESS_CONFIG)
        return text

    def run_page_with_layout(self, image: QImage, lang: str = "fra+eng") -> list[dict]:
        """Return OCR results with bounding boxes (word level)."""
        if not self._available:
            return []
        pil_image = self._qimage_to_pil(image)
        data = pytesseract.image_to_data(
            pil_image, lang=lang,
            output_type=pytesseract.Output.DICT,
        )
        results = []
        for i, text in enumerate(data["text"]):
            if text.strip():
                results.append({
                    "text": text,
                    "x": data["left"][i],
                    "y": data["top"][i],
                    "w": data["width"][i],
                    "h": data["height"][i],
                    "conf": data["conf"][i],
                })
        return results

    def run_page_lines(self, image: QImage, lang: str = "fra+eng",
                       dpi: int = 288) -> list[dict]:
        """Return OCR results grouped by line, with color detection.

        Each item: {text, x, y, w, h, conf, color, x_size}
        x_size: Tesseract em-height in pixels (for accurate font size mapping).
        Coordinates are in pixels of the source image.

        Args:
            dpi: Actual resolution of *image* in DPI.  Must match the zoom used
                 when rendering the page (default 288 = 3× screen at 96 DPI).
                 Wrong DPI causes Tesseract to misclassify tall glyphs (€, $) as
                 graphics and skip them entirely.
        """
        if not self._available:
            return []
        config = f"{self._TESS_LINES_CONFIG_BASE} --dpi {dpi}"
        pil_image = self._preprocess(self._qimage_to_pil(image))
        # Embed DPI in the PIL image so pytesseract's internal TIFF/PNG export
        # carries the correct value (reinforces the --dpi flag in the config).
        pil_image.info["dpi"] = (dpi, dpi)
        data = pytesseract.image_to_data(
            pil_image, lang=lang,
            output_type=pytesseract.Output.DICT,
            config=config,
        )

        # Collect x_size (em-height in px) per line from hOCR for accurate font sizing.
        # Two-step parsing: (1) extract each ocr_line title attribute, then (2) parse
        # bbox and x_size from that attribute — avoids nested quantifiers and the
        # catastrophic backtracking they would cause on large documents.
        line_xsizes: dict = {}  # (y_top, y_bot) → x_size
        try:
            # Use a separate PIL copy so pytesseract cannot mutate pil_image.info
            # between the two Tesseract passes.
            hocr_image = pil_image.copy()
            hocr_image.info["dpi"] = (dpi, dpi)
            hocr = pytesseract.image_to_pdf_or_hocr(
                hocr_image, lang=lang, extension="hocr", config=config,
            )
            hocr_str = hocr.decode("utf-8", errors="ignore")
            # Step 1 — find every ocr_line title="…" attribute
            for m_title in re.finditer(
                r"class=['\"]ocr_line['\"][^>]*title=['\"]([^'\"]+)['\"]",
                hocr_str,
            ):
                title = m_title.group(1)
                # Step 2 — parse bbox and x_size independently within the title
                m_bbox  = re.search(r"bbox\s+\d+\s+(\d+)\s+\d+\s+(\d+)", title)
                m_xsize = re.search(r"x_size\s+([\d.]+)", title)
                if m_bbox and m_xsize:
                    y0  = int(m_bbox.group(1))
                    y1  = int(m_bbox.group(2))
                    xsz = float(m_xsize.group(1))
                    line_xsizes[(y0, y1)] = xsz
        except Exception:
            pass

        def _find_xsize(y_top: int, y_bot: int) -> float:
            """Return x_size of the hOCR line whose y-range is closest to (y_top, y_bot)."""
            best, best_d = 0.0, float("inf")
            for (y0, y1), xsz in line_xsizes.items():
                d = abs(y0 - y_top) + abs(y1 - y_bot)
                if d < best_d:
                    best_d, best = d, xsz
            return best

        # Group words by (block_num, par_num, line_num)
        # Key insight: Tesseract marks punctuation/separators like "-" as conf=-1 at
        # word level (level=5) even though they ARE real text characters.  We must
        # include level-5 entries with non-empty text regardless of confidence so that
        # symbols like "-", "€", "$" are never silently dropped.
        buckets: dict = defaultdict(lambda: {
            "words": [], "x0": [], "y0": [], "x1": [], "y1": [], "conf": []
        })
        levels = data.get("level", [])
        for i, text in enumerate(data["text"]):
            conf_val = int(data["conf"][i])
            level = levels[i] if i < len(levels) else 5
            # Skip page/block/para/line container rows (level < 5); they always have conf=-1
            # and carry no text.  For word rows (level=5), keep any non-empty text even
            # when conf=-1 (separator/punctuation tokens: "-", "€", "$", etc.).
            if level < 5:
                continue
            if conf_val < 0 and not text.strip():
                continue
            key = (data["block_num"][i], data["par_num"][i], data["line_num"][i])
            x, y, w, h = data["left"][i], data["top"][i], data["width"][i], data["height"][i]
            buckets[key]["words"].append(text)
            buckets[key]["x0"].append(x)
            buckets[key]["y0"].append(y)
            buckets[key]["x1"].append(x + w)
            buckets[key]["y1"].append(y + h)
            # Use 0 for separator tokens so they don't drag down line average confidence
            buckets[key]["conf"].append(max(0, conf_val))

        results = []
        for key in sorted(buckets.keys()):
            b = buckets[key]
            text = " ".join(t for t in b["words"] if t.strip())
            # Tesseract LSTM (fra) substitutes — / – for - because French
            # typography uses cadratins for dialogue/lists.  Normalise back.
            text = text.replace("\u2014", "-").replace("\u2013", "-")
            if not text.strip():
                continue
            x  = min(b["x0"])
            y  = min(b["y0"])
            w  = max(b["x1"]) - x
            h  = max(b["y1"]) - y
            conf = int(sum(b["conf"]) / len(b["conf"])) if b["conf"] else 0
            # Drop lines that are pure noise (no real OCR confidence at all)
            if conf < 5:
                continue
            x_size = _find_xsize(y, y + h)
            color = self._detect_text_color(image, x, y, w, h)
            results.append({"text": text, "x": x, "y": y, "w": w, "h": h,
                             "conf": conf, "color": color, "x_size": x_size})
        return results

    @staticmethod
    def _preprocess(pil_image: "Image.Image") -> "Image.Image":
        """Prepare image for Tesseract: grayscale → autocontrast → sharpen.

        autocontrast stretches the histogram to the full 0-255 range, which
        normalises dark-text-on-grey-background as well as black-on-white.
        Works on images already rendered at high zoom (≥ 2×).
        """
        from PIL import ImageEnhance, ImageFilter, ImageOps

        # Grayscale
        img = pil_image.convert("L")

        # autocontrast: maps the darkest 2 % of pixels → 0 and lightest 2 % → 255.
        # This handles grey backgrounds and low-contrast scans naturally.
        img = ImageOps.autocontrast(img, cutoff=2)

        # Sharpen edges (helps with slightly blurry renders)
        img = ImageEnhance.Sharpness(img).enhance(2.0)

        # Mild unsharp-mask to accentuate character strokes
        img = img.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=3))

        return img

    @staticmethod
    def _detect_text_color(image: QImage, x: int, y: int, w: int, h: int) -> str:
        """Sample the dominant non-background color inside a bounding box.

        Returns '#rrggbb'. Falls back to black if the region is mostly white.
        """
        try:
            from PIL import Image as PilImage
            pil = image.convertToFormat(QImage.Format.Format_RGBA8888)
            ptr = pil.bits()
            raw = bytes(ptr)
            img = PilImage.frombytes("RGBA", (pil.width(), pil.height()), raw).convert("RGB")

            # Clamp bbox to image bounds
            ix0 = max(0, x)
            iy0 = max(0, y)
            ix1 = min(img.width,  x + w)
            iy1 = min(img.height, y + h)
            if ix1 <= ix0 or iy1 <= iy0:
                return "#000000"

            region = img.crop((ix0, iy0, ix1, iy1))
            pixels = list(region.getdata())

            # Keep "dark" pixels (sum of RGB < 400 ≈ not near-white/background)
            dark = [(r, g, b) for r, g, b in pixels if r + g + b < 400]
            if not dark:
                return "#000000"

            avg_r = int(sum(p[0] for p in dark) / len(dark))
            avg_g = int(sum(p[1] for p in dark) / len(dark))
            avg_b = int(sum(p[2] for p in dark) / len(dark))
            return f"#{avg_r:02x}{avg_g:02x}{avg_b:02x}"
        except Exception:
            return "#000000"

    @staticmethod
    def available_languages() -> list[str]:
        if not HAS_TESSERACT:
            return []
        try:
            output = pytesseract.get_languages()
            return sorted(output)
        except Exception:
            return ["fra", "eng"]

    def _check_available(self) -> bool:
        if not HAS_TESSERACT:
            return False
        try:
            pytesseract.get_tesseract_version()
            return True
        except Exception:
            return False

    @staticmethod
    def _qimage_to_pil(image: QImage) -> "Image.Image":
        from PIL import Image
        image = image.convertToFormat(QImage.Format.Format_RGBA8888)
        w, h = image.width(), image.height()
        ptr = image.bits()
        arr = bytes(ptr)
        return Image.frombytes("RGBA", (w, h), arr)
