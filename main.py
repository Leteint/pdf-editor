"""
PDF Editor — point d'entrée principal.
"""
import sys
import os

# Ensure the project root is in the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication, QToolTip
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPalette, QColor

from ui.main_window import MainWindow
from utils.config import Config
from utils.font_manager import load_cached_fonts
from utils.i18n import set_language
from utils.tesseract_setup import run_first_time_setup


def _run_image_to_pdf(image_path: str) -> None:
    """Minimal conversion mode triggered by the Windows right-click context menu."""
    from PySide6.QtWidgets import QApplication, QMessageBox
    app = QApplication(sys.argv)  # noqa: F841 — needed for Qt dialogs

    if not os.path.isfile(image_path):
        QMessageBox.critical(None, "PDF Editor",
                             f"Fichier introuvable :\n{image_path}")
        return

    base     = os.path.splitext(image_path)[0]
    pdf_path = base + ".pdf"
    # Auto-increment if the output file already exists
    counter  = 1
    while os.path.exists(pdf_path):
        pdf_path = f"{base}_{counter}.pdf"
        counter += 1

    try:
        # Try img2pdf first (lossless JPEG, native PNG/TIFF multi-page)
        try:
            import img2pdf
            pdf_bytes = img2pdf.convert(image_path)
        except Exception:
            # Fallback: Pillow (handles WebP, BMP…)
            from PIL import Image
            import io as _io
            bio = _io.BytesIO()
            with Image.open(image_path) as img:
                frames: list = []
                try:
                    while True:
                        frames.append(img.copy().convert("RGB"))
                        img.seek(img.tell() + 1)
                except EOFError:
                    pass
                if not frames:
                    frames = [img.convert("RGB")]
                if len(frames) == 1:
                    frames[0].save(bio, format="PDF")
                else:
                    frames[0].save(bio, format="PDF",
                                   save_all=True, append_images=frames[1:])
            pdf_bytes = bio.getvalue()

        with open(pdf_path, "wb") as fh:
            fh.write(pdf_bytes)

        QMessageBox.information(
            None, "PDF Editor",
            f"PDF créé avec succès :\n{os.path.basename(pdf_path)}\n\n"
            f"Dossier : {os.path.dirname(pdf_path)}"
        )
    except Exception as exc:
        QMessageBox.critical(None, "PDF Editor",
                             f"Erreur lors de la conversion :\n{exc}")


def _run_combine(file_path: str) -> None:
    """Accumulate files from multi-select right-click, then open the app.

    Windows launches one process per selected file nearly simultaneously.
    The first process (coordinator) waits ~900 ms for the others to write
    their paths to a shared temp file, then launches the main app in
    combine mode (--open-combine).
    """
    import time, tempfile

    tmp_dir    = tempfile.gettempdir()
    bucket     = int(time.time()) // 2           # 2-second time bucket
    list_file  = os.path.join(tmp_dir, f"pdfeditor_combine_{bucket}.txt")
    coord_file = os.path.join(tmp_dir, f"pdfeditor_combine_{bucket}.lock")

    # Append this file to the shared list
    try:
        with open(list_file, "a", encoding="utf-8") as f:
            f.write(file_path + "\n")
    except Exception:
        pass

    # Try to become coordinator — only the first process wins
    try:
        fd = os.open(coord_file, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.close(fd)
    except FileExistsError:
        return  # Another process is already the coordinator

    # Wait for other parallel processes to write their files
    time.sleep(0.9)

    # Read the accumulated list
    try:
        with open(list_file, "r", encoding="utf-8") as f:
            raw = [p.strip() for p in f if p.strip()]
    except Exception:
        raw = [file_path]

    # Deduplicate, keep only existing files
    seen: set[str] = set()
    paths: list[str] = []
    for p in raw:
        if p not in seen and os.path.isfile(p):
            seen.add(p)
            paths.append(p)

    # Cleanup temp files
    for fp in (list_file, coord_file):
        try:
            os.unlink(fp)
        except Exception:
            pass

    if not paths:
        return

    # Launch the main app in combine mode
    if getattr(sys, "frozen", False):
        cmd = [sys.executable, "--open-combine"] + paths
    else:
        main_py = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py")
        cmd = [sys.executable, main_py, "--open-combine"] + paths

    import subprocess
    subprocess.Popen(cmd)


def _check_license_at_startup(app) -> bool:
    """
    Validate license before showing the main window.
    Returns True if the app should continue, False if user quit.
    """
    from utils.license import get_stored_key, check_license, LicenseResult
    from ui.dialogs.license_dialog import LicenseDialog

    key = get_stored_key()

    if key:
        result = check_license(key)
        if result.valid:
            return True
        # Invalid — show dialog with reason
        msg = result.reason
    else:
        msg = ""

    # Show activation dialog
    dlg = LicenseDialog(message=msg)
    return dlg.exec() == LicenseDialog.DialogCode.Accepted


def main() -> None:
    # ── Right-click "Transformer en PDF" mode ────────────────────────────
    if "--to-pdf" in sys.argv:
        idx = sys.argv.index("--to-pdf")
        image_path = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else ""
        _run_image_to_pdf(image_path)
        return

    # ── Right-click "Combiner dans PDF Editor" mode ───────────────────────
    if "--combine" in sys.argv:
        idx = sys.argv.index("--combine")
        file_path = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else ""
        _run_combine(file_path)
        return

    # High-DPI support
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("PDF Editor")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("OpenPDFEditor")

    config = Config()
    set_language(config.get("language", "fr"))

    # Load theme
    theme_path = os.path.join(
        os.path.dirname(__file__),
        "assets", "themes",
        f"{config.get('theme', 'dark')}.qss",
    )
    if os.path.exists(theme_path):
        with open(theme_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())

    # Force tooltip colors (QSS is ignored by Windows native style for tooltips)
    tt_palette = QToolTip.palette()
    tt_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#fffde7"))
    tt_palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#1a1a1a"))
    QToolTip.setPalette(tt_palette)

    # Load previously downloaded fonts from local cache
    load_cached_fonts()

    # ── License check ────────────────────────────────────────────────────
    if not _check_license_at_startup(app):
        sys.exit(0)

    # First-run: propose Tesseract OCR installation if not already present
    run_first_time_setup(config)

    # Activate Windows shell integrations by default
    try:
        from utils.shell_integration import (
            is_registered, register,
            is_combine_registered, register_combine,
        )
        if not is_registered():
            register()
        if not is_combine_registered():
            register_combine()
    except Exception:
        pass  # Non-Windows or registry error — silently skip

    # Collect combine paths before creating the window
    combine_paths: list[str] = []
    if "--open-combine" in sys.argv:
        idx = sys.argv.index("--open-combine")
        combine_paths = [p for p in sys.argv[idx + 1:] if os.path.isfile(p)]

    window = MainWindow(config)
    window.show()

    # Open combine dialog with pre-loaded files (from right-click multi-select)
    if combine_paths:
        window.open_combine(combine_paths)
        sys.exit(app.exec())

    # Open file passed as argument
    if len(sys.argv) > 1 and not sys.argv[1].startswith("--") and os.path.isfile(sys.argv[1]):
        window.open_file(sys.argv[1])

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
