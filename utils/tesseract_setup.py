"""
Tesseract first-run setup — portable app edition.

Called once at startup when tesseract.exe cannot be found.
Offers the user to download and install Tesseract silently.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import urllib.request
from typing import Optional

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
    QComboBox, QDialogButtonBox, QProgressDialog, QMessageBox,
)
from PySide6.QtCore import Qt

# ---------------------------------------------------------------------------
# Tesseract installer — UB-Mannheim official Windows build
# ---------------------------------------------------------------------------
_TESS_VERSION = "5.3.4.20240926"
_TESS_URL = (
    f"https://github.com/UB-Mannheim/tesseract/releases/download/"
    f"v{_TESS_VERSION}/tesseract-ocr-w64-setup-{_TESS_VERSION}.exe"
)
_TESSDATA_BASE = "https://raw.githubusercontent.com/tesseract-ocr/tessdata_fast/main/"

_LANGUAGES = [
    ("ara",     "Arabic / عربي"),
    ("ces",     "Czech / Čeština"),
    ("dan",     "Danish / Dansk"),
    ("deu",     "German / Deutsch"),
    ("ell",     "Greek / Ελληνικά"),
    ("eng",     "English"),
    ("spa",     "Spanish / Español"),
    ("fin",     "Finnish / Suomi"),
    ("fra",     "Français"),
    ("heb",     "Hebrew / עברית"),
    ("hun",     "Hungarian / Magyar"),
    ("ita",     "Italian / Italiano"),
    ("jpn",     "Japanese / 日本語"),
    ("kor",     "Korean / 한국어"),
    ("nld",     "Dutch / Nederlands"),
    ("nor",     "Norwegian / Norsk"),
    ("pol",     "Polish / Polski"),
    ("por",     "Portuguese / Português"),
    ("ron",     "Romanian / Română"),
    ("rus",     "Russian / Русский"),
    ("chi_sim", "Chinese Simplified / 简体中文"),
    ("swe",     "Swedish / Svenska"),
    ("tur",     "Turkish / Türkçe"),
    ("ukr",     "Ukrainian / Українська"),
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _find_tesseract() -> Optional[str]:
    """Return path to tesseract.exe if already installed, else None."""
    if sys.platform != "win32":
        return None

    import winreg
    for hive in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
        for sub in (r"SOFTWARE\Tesseract-OCR", r"SOFTWARE\WOW6432Node\Tesseract-OCR"):
            try:
                with winreg.OpenKey(hive, sub) as k:
                    install_dir, _ = winreg.QueryValueEx(k, "InstallDir")
                    candidate = os.path.join(install_dir, "tesseract.exe")
                    if os.path.isfile(candidate):
                        return candidate
            except OSError:
                pass

    for path in (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Tesseract-OCR\tesseract.exe"),
    ):
        if os.path.isfile(path):
            return path
    return None


def _system_lang_code() -> str:
    """Return the Tesseract language code that best matches the Windows UI language."""
    if sys.platform != "win32":
        return "eng"
    try:
        import ctypes
        lcid = ctypes.windll.kernel32.GetSystemDefaultLCID() & 0x3FF  # primary only
        _map = {
            0x001: "ara", 0x004: "chi_sim", 0x005: "ces", 0x006: "dan",
            0x007: "deu", 0x008: "ell",     0x009: "eng", 0x00A: "spa",
            0x00B: "fin", 0x00C: "fra",     0x00D: "heb", 0x00E: "hun",
            0x010: "ita", 0x011: "jpn",     0x012: "kor", 0x013: "nld",
            0x014: "nor", 0x015: "pol",     0x016: "por", 0x018: "ron",
            0x019: "rus", 0x01D: "swe",     0x01F: "tur", 0x022: "ukr",
        }
        return _map.get(lcid, "eng")
    except Exception:
        return "eng"


def _download(url: str, dest: str, label: str, progress: QProgressDialog) -> bool:
    """Download *url* to *dest*, updating *progress*. Returns True on success."""
    try:
        progress.setLabelText(label)
        with urllib.request.urlopen(url, timeout=60) as resp:
            total = int(resp.headers.get("Content-Length", 0))
            progress.setMaximum(max(total, 1))
            downloaded = 0
            chunk = 65536
            with open(dest, "wb") as fh:
                while True:
                    if progress.wasCanceled():
                        return False
                    data = resp.read(chunk)
                    if not data:
                        break
                    fh.write(data)
                    downloaded += len(data)
                    progress.setValue(downloaded)
        return True
    except Exception as exc:
        QMessageBox.critical(None, "Erreur de téléchargement", str(exc))
        return False


def _write_config_tesseract(path: str) -> None:
    """Persist the Tesseract exe path in the app config.json."""
    try:
        from utils.config import Config
        cfg = Config()
        cfg.set("tesseract_path", path)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Setup dialog
# ---------------------------------------------------------------------------

class _TesseractSetupDialog(QDialog):
    def __init__(self, already_installed: bool, default_lang: str) -> None:
        super().__init__(None, Qt.WindowType.Dialog)
        self.setWindowTitle("Reconnaissance de caractères (OCR) — Configuration")
        self.setMinimumWidth(500)
        self._already_installed = already_installed
        self._build(default_lang)

    def _build(self, default_lang: str) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        title = QLabel("<b>Tesseract OCR — moteur de reconnaissance de texte</b>")
        layout.addWidget(title)

        desc = QLabel(
            "Tesseract est un logiciel libre (Apache 2.0) qui permet à PDF Editor "
            "d'extraire le texte contenu dans les pages numérisées.<br>"
            "Il sera téléchargé depuis GitHub (~50 MB) puis installé automatiquement."
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)

        if self._already_installed:
            caption = "Tesseract est déjà installé — vérifier / compléter les modèles de langue"
        else:
            caption = "Installer Tesseract OCR (recommandé)"

        self._chk = QCheckBox(caption)
        self._chk.setChecked(True)
        self._chk.toggled.connect(self._on_toggle)
        layout.addWidget(self._chk)

        lang_row = QHBoxLayout()
        lang_row.addWidget(QLabel("Langue OCR principale :"))
        self._combo = QComboBox()
        default_idx = 5  # English fallback
        for i, (code, label) in enumerate(_LANGUAGES):
            self._combo.addItem(label, code)
            if code == default_lang:
                default_idx = i
        self._combo.setCurrentIndex(default_idx)
        lang_row.addWidget(self._combo)
        lang_row.addStretch()
        layout.addLayout(lang_row)

        note = QLabel(
            "<small><i>L'anglais sera toujours inclus comme langue de secours.</i></small>"
        )
        layout.addWidget(note)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _on_toggle(self, checked: bool) -> None:
        self._combo.setEnabled(checked)

    @property
    def install_requested(self) -> bool:
        return self._chk.isChecked()

    @property
    def selected_lang(self) -> str:
        return self._combo.currentData()


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run_first_time_setup(config) -> None:
    """
    Show the Tesseract setup dialog if Tesseract is not yet configured.
    Call this after QApplication is created but before the main window is shown.
    Only runs on Windows; silently skipped on Linux/macOS.
    """
    if sys.platform != "win32":
        return

    # Already configured in config.json and exe exists — nothing to do.
    configured_path = config.get("tesseract_path", "")
    if configured_path and os.path.isfile(configured_path):
        return

    existing = _find_tesseract()
    default_lang = _system_lang_code()

    dlg = _TesseractSetupDialog(
        already_installed=(existing is not None),
        default_lang=default_lang,
    )
    if dlg.exec() != QDialog.DialogCode.Accepted or not dlg.install_requested:
        # User declined — if Tesseract exists, still save the path silently.
        if existing:
            _write_config_tesseract(existing)
        return

    lang_code = dlg.selected_lang
    _do_install(existing, lang_code, config)


def _do_install(existing_path: Optional[str], lang_code: str, config) -> None:
    """Download Tesseract if needed, then download the language model."""
    progress = QProgressDialog("Préparation…", "Annuler", 0, 100, None)
    progress.setWindowTitle("Installation de Tesseract OCR")
    progress.setWindowModality(Qt.WindowModality.ApplicationModal)
    progress.setMinimumWidth(420)
    progress.show()

    tess_dir = os.path.dirname(existing_path) if existing_path else \
               r"C:\Program Files\Tesseract-OCR"

    # ── 1. Install Tesseract if not present ──────────────────────────────
    if not existing_path:
        tmp_installer = os.path.join(tempfile.gettempdir(), "tesseract-setup.exe")
        progress.setMaximum(0)  # busy indicator during download
        ok = _download(_TESS_URL, tmp_installer,
                       "Téléchargement de Tesseract OCR (~50 MB)…", progress)
        if not ok or progress.wasCanceled():
            progress.close()
            return

        progress.setLabelText("Installation de Tesseract OCR…")
        progress.setMaximum(0)
        try:
            subprocess.run(
                [tmp_installer, "/S", f"/D={tess_dir}"],
                check=True, timeout=300,
            )
        except Exception as exc:
            progress.close()
            QMessageBox.critical(
                None, "Erreur",
                f"L'installation de Tesseract a échoué :\n{exc}\n\n"
                "Vous pouvez l'installer manuellement depuis :\n"
                "https://github.com/UB-Mannheim/tesseract/releases"
            )
            return

    tessdata_dir = os.path.join(tess_dir, "tessdata")
    os.makedirs(tessdata_dir, exist_ok=True)

    # ── 2. Download English model (fallback) ─────────────────────────────
    eng_file = os.path.join(tessdata_dir, "eng.traineddata")
    if lang_code != "eng" and not os.path.isfile(eng_file):
        tmp = os.path.join(tempfile.gettempdir(), "eng.traineddata")
        progress.setMaximum(0)
        if _download(_TESSDATA_BASE + "eng.traineddata", tmp,
                     "Téléchargement du modèle OCR (eng)…", progress):
            try:
                import shutil; shutil.copy(tmp, eng_file)
            except Exception:
                pass

    # ── 3. Download selected language model ──────────────────────────────
    lang_file = os.path.join(tessdata_dir, f"{lang_code}.traineddata")
    if not os.path.isfile(lang_file):
        tmp = os.path.join(tempfile.gettempdir(), f"{lang_code}.traineddata")
        progress.setMaximum(0)
        ok = _download(
            _TESSDATA_BASE + f"{lang_code}.traineddata", tmp,
            f"Téléchargement du modèle OCR ({lang_code})…", progress,
        )
        if ok:
            try:
                import shutil; shutil.copy(tmp, lang_file)
            except Exception:
                pass

    progress.close()

    # ── 4. Persist path ───────────────────────────────────────────────────
    tess_exe = os.path.join(tess_dir, "tesseract.exe")
    if os.path.isfile(tess_exe):
        _write_config_tesseract(tess_exe)
        QMessageBox.information(
            None, "Tesseract OCR",
            "Tesseract OCR a été installé avec succès.\n"
            "La reconnaissance de caractères est maintenant disponible."
        )
    else:
        QMessageBox.warning(
            None, "Tesseract OCR",
            "L'installation semble incomplète (tesseract.exe introuvable).\n"
            "Vous pouvez l'installer manuellement depuis :\n"
            "https://github.com/UB-Mannheim/tesseract/releases"
        )
