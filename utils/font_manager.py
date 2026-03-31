"""
Font manager — detects if a font is installed on the system,
and offers to download free/open-source equivalents from Google Fonts.
"""
from __future__ import annotations

import os
import re
import urllib.request
import zipfile
import tempfile
import shutil
from typing import Optional

from PySide6.QtGui import QFontDatabase, QFont


# ------------------------------------------------------------------
# Mapping: common PDF embedded font names → Google Fonts equivalent
# ------------------------------------------------------------------

FONT_MAP: dict[str, tuple[str, str]] = {
    # PDF name (lower, stripped)  →  (Google Fonts name, display name)
    "arial":            ("Arial",          "Arial (Windows built-in)"),
    "helvetica":        ("Liberation Sans", "Liberation Sans (Helvetica équivalent)"),
    "timesnewroman":    ("Tinos",          "Tinos (Times New Roman équivalent)"),
    "times":            ("Tinos",          "Tinos (Times New Roman équivalent)"),
    "couriernew":       ("Cousine",        "Cousine (Courier New équivalent)"),
    "courier":          ("Cousine",        "Cousine (Courier New équivalent)"),
    "georgia":          ("Lora",           "Lora (Georgia-style serif)"),
    "verdana":          ("Noto Sans",      "Noto Sans (Verdana-style)"),
    "trebuchetms":      ("Cabin",          "Cabin (Trebuchet-style)"),
    "calibri":          ("Carlito",        "Carlito (Calibri équivalent)"),
    "cambria":          ("Caladea",        "Caladea (Cambria équivalent)"),
    "garamond":         ("EB Garamond",    "EB Garamond"),
    "palatino":         ("GFS Didot",      "GFS Didot (Palatino-style)"),
    "futura":           ("Jost",           "Jost (Futura-style)"),
    "gillsans":         ("Nunito",         "Nunito (Gill Sans-style)"),
    "myriadpro":        ("Raleway",        "Raleway (Myriad-style)"),
    "franklingothic":   ("Oswald",         "Oswald (Franklin Gothic-style)"),
    "notosans":         ("Noto Sans",      "Noto Sans"),
    "opensans":         ("Open Sans",      "Open Sans"),
    "roboto":           ("Roboto",         "Roboto"),
    "lato":             ("Lato",           "Lato"),
    "montserrat":       ("Montserrat",     "Montserrat"),
    "sourcesanspro":    ("Source Sans 3",  "Source Sans 3"),
    "ubuntu":           ("Ubuntu",         "Ubuntu"),
    "merriweather":     ("Merriweather",   "Merriweather"),
    "playfairdisplay":  ("Playfair Display","Playfair Display"),
}

# Google Fonts direct ZIP download URLs (subset — popular fonts)
GOOGLE_FONTS_URLS: dict[str, str] = {
    "Tinos":            "https://fonts.google.com/download?family=Tinos",
    "Cousine":          "https://fonts.google.com/download?family=Cousine",
    "Carlito":          "https://fonts.google.com/download?family=Carlito",
    "Caladea":          "https://fonts.google.com/download?family=Caladea",
    "Liberation Sans":  "https://fonts.google.com/download?family=Liberation+Sans",
    "EB Garamond":      "https://fonts.google.com/download?family=EB+Garamond",
    "Lora":             "https://fonts.google.com/download?family=Lora",
    "Cabin":            "https://fonts.google.com/download?family=Cabin",
    "Jost":             "https://fonts.google.com/download?family=Jost",
    "Nunito":           "https://fonts.google.com/download?family=Nunito",
    "Raleway":          "https://fonts.google.com/download?family=Raleway",
    "Oswald":           "https://fonts.google.com/download?family=Oswald",
    "Noto Sans":        "https://fonts.google.com/download?family=Noto+Sans",
    "Open Sans":        "https://fonts.google.com/download?family=Open+Sans",
    "Roboto":           "https://fonts.google.com/download?family=Roboto",
    "Lato":             "https://fonts.google.com/download?family=Lato",
    "Montserrat":       "https://fonts.google.com/download?family=Montserrat",
    "Source Sans 3":    "https://fonts.google.com/download?family=Source+Sans+3",
    "Ubuntu":           "https://fonts.google.com/download?family=Ubuntu",
    "Merriweather":     "https://fonts.google.com/download?family=Merriweather",
    "Playfair Display": "https://fonts.google.com/download?family=Playfair+Display",
}

# Local font cache dir
FONT_CACHE_DIR = os.path.join(os.path.expanduser("~"), ".pdf_editor", "fonts")


def _normalise(name: str) -> str:
    """Normalise font name for lookup."""
    return re.sub(r"[\s\-_,]", "", name).lower()


def is_font_available(family: str) -> bool:
    """Return True if the font family is installed on this system."""
    db = QFontDatabase()
    available = [f.lower() for f in db.families()]
    return family.lower() in available


def find_best_family(pdf_font_name: str) -> tuple[str, bool, str]:
    """
    Given a raw PDF font name, return:
      (best_family, is_exact_match, note)

    If the exact font is installed → return it directly.
    If a known open-source equivalent exists → return that.
    Otherwise → return "Arial" as fallback.
    """
    db = QFontDatabase()
    available_lower = {f.lower(): f for f in db.families()}

    # 1. Exact or partial match in installed fonts
    cleaned = _normalise(pdf_font_name)
    for avail_lower, avail_name in available_lower.items():
        if _normalise(avail_name) == cleaned or cleaned.startswith(_normalise(avail_name)):
            return avail_name, True, f"Police installée : {avail_name}"

    # 2. Known equivalence map
    equiv = FONT_MAP.get(cleaned)
    if not equiv:
        # Try prefix match in map
        for key, val in FONT_MAP.items():
            if cleaned.startswith(key) or key.startswith(cleaned):
                equiv = val
                break

    if equiv:
        gf_name, display = equiv
        # Check if equivalent is already installed
        if gf_name.lower() in available_lower:
            note = f"Équivalent installé : {gf_name} (original : {pdf_font_name})"
            return available_lower[gf_name.lower()], False, note

        # Check if we cached it locally
        cached = _find_in_cache(gf_name)
        if cached:
            _load_font_file(cached)
            if gf_name.lower() in {f.lower() for f in QFontDatabase().families()}:
                return gf_name, False, f"Équivalent chargé depuis le cache : {gf_name}"

        return gf_name, False, f"Équivalent disponible : {display} (non installé — téléchargement proposé)"

    # 3. Fallback
    return "Arial", False, f"Police inconnue '{pdf_font_name}' → Arial utilisé"


def can_download(family: str) -> bool:
    """Return True if we have a download URL for this font."""
    return family in GOOGLE_FONTS_URLS


def download_font(family: str, progress_cb=None) -> bool:
    """
    Download a Google Font ZIP and install it into the local font cache.
    progress_cb(percent: int) is called during download.
    Returns True on success.
    """
    url = GOOGLE_FONTS_URLS.get(family)
    if not url:
        return False

    os.makedirs(FONT_CACHE_DIR, exist_ok=True)
    tmp = tempfile.mkdtemp()
    zip_path = os.path.join(tmp, "font.zip")

    try:
        def _reporthook(count, block_size, total_size):
            if progress_cb and total_size > 0:
                progress_cb(min(99, int(count * block_size * 100 / total_size)))

        urllib.request.urlretrieve(url, zip_path, reporthook=_reporthook)

        with zipfile.ZipFile(zip_path, "r") as z:
            font_dir = os.path.join(FONT_CACHE_DIR, _normalise(family))
            os.makedirs(font_dir, exist_ok=True)
            for name in z.namelist():
                if name.lower().endswith((".ttf", ".otf")):
                    z.extract(name, font_dir)

        # Load the fonts into Qt
        loaded = _load_fonts_from_dir(os.path.join(FONT_CACHE_DIR, _normalise(family)))
        if progress_cb:
            progress_cb(100)
        return loaded > 0

    except Exception:
        return False
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def load_cached_fonts() -> None:
    """Load all previously downloaded fonts from cache on startup."""
    if not os.path.isdir(FONT_CACHE_DIR):
        return
    for sub in os.listdir(FONT_CACHE_DIR):
        _load_fonts_from_dir(os.path.join(FONT_CACHE_DIR, sub))


def _load_fonts_from_dir(directory: str) -> int:
    count = 0
    if not os.path.isdir(directory):
        return 0
    for root, _, files in os.walk(directory):
        for fname in files:
            if fname.lower().endswith((".ttf", ".otf")):
                path = os.path.join(root, fname)
                if QFontDatabase.addApplicationFont(path) >= 0:
                    count += 1
    return count


def _load_font_file(path: str) -> bool:
    return QFontDatabase.addApplicationFont(path) >= 0


def _find_in_cache(family: str) -> Optional[str]:
    """Find any .ttf/.otf in the cache for the given family."""
    font_dir = os.path.join(FONT_CACHE_DIR, _normalise(family))
    if not os.path.isdir(font_dir):
        return None
    for root, _, files in os.walk(font_dir):
        for f in files:
            if f.lower().endswith((".ttf", ".otf")):
                return os.path.join(root, f)
    return None
