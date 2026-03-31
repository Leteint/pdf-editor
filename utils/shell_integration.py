"""
Windows shell integration — adds/removes right-click context menu entries:
  • "Transformer en PDF"       — single image → PDF (image extensions)
  • "Combiner dans PDF Editor" — multi-select files → OrganizeDialog

Registry location: HKEY_CURRENT_USER (no admin rights required).
"""
from __future__ import annotations
import os
import sys

EXTENSIONS = [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"]
_VERB  = "TransformerEnPDF"
_LABEL = "Transformer en PDF - PDF EDITOR"

COMBINE_EXTENSIONS = [".pdf", ".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"]
_COMBINE_VERB  = "CombinerPDFEditor"
_COMBINE_LABEL = "Combiner dans PDF Editor"


def _exe_command() -> str:
    """Return the shell command string to invoke the conversion."""
    if getattr(sys, "frozen", False):
        exe = sys.executable
        return f'"{exe}" --to-pdf "%1"'
    else:
        python = sys.executable
        main   = os.path.normpath(
            os.path.join(os.path.dirname(__file__), "..", "main.py")
        )
        return f'"{python}" "{main}" --to-pdf "%1"'


def _exe_icon() -> str:
    """Return the icon path for the context menu entry.
    Frozen: use the embedded exe icon. Dev: use assets/icons/icon.ico."""
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}",0'
    icon = os.path.normpath(
        os.path.join(os.path.dirname(__file__), "..", "assets", "icons", "icon.ico")
    )
    if os.path.exists(icon):
        return f'"{icon}",0'
    return ""


def register() -> None:
    """Write registry entries for all supported image extensions."""
    import winreg
    cmd  = _exe_command()
    icon = _exe_icon()
    for ext in EXTENSIONS:
        base = rf"Software\Classes\SystemFileAssociations\{ext}\shell\{_VERB}"
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, base) as k:
            winreg.SetValueEx(k, "",       0, winreg.REG_SZ, _LABEL)
            if icon:
                winreg.SetValueEx(k, "Icon", 0, winreg.REG_SZ, icon)
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, base + r"\command") as k:
            winreg.SetValueEx(k, "", 0, winreg.REG_SZ, cmd)


def unregister() -> None:
    """Remove registry entries for all supported image extensions."""
    import winreg
    for ext in EXTENSIONS:
        base = rf"Software\Classes\SystemFileAssociations\{ext}\shell\{_VERB}"
        for sub in (r"\command", ""):
            try:
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, base + sub)
            except FileNotFoundError:
                pass


def is_registered() -> bool:
    """Return True if the context menu is currently registered."""
    import winreg
    try:
        key = rf"Software\Classes\SystemFileAssociations\.jpg\shell\{_VERB}"
        winreg.OpenKey(winreg.HKEY_CURRENT_USER, key).Close()
        return True
    except FileNotFoundError:
        return False


# ---------------------------------------------------------------------------
# Combine multi-select: "Combiner dans PDF Editor"
# ---------------------------------------------------------------------------

def _combine_command() -> str:
    """Return the shell command string for the combine context menu entry."""
    if getattr(sys, "frozen", False):
        exe = sys.executable
        return f'"{exe}" --combine "%1"'
    python = sys.executable
    main   = os.path.normpath(
        os.path.join(os.path.dirname(__file__), "..", "main.py")
    )
    return f'"{python}" "{main}" --combine "%1"'


def register_combine() -> None:
    """Write registry entries for the combine multi-select context menu."""
    import winreg
    cmd  = _combine_command()
    icon = _exe_icon()
    for ext in COMBINE_EXTENSIONS:
        base = rf"Software\Classes\SystemFileAssociations\{ext}\shell\{_COMBINE_VERB}"
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, base) as k:
            winreg.SetValueEx(k, "",                0, winreg.REG_SZ, _COMBINE_LABEL)
            winreg.SetValueEx(k, "MultiSelectModel", 0, winreg.REG_SZ, "Player")
            if icon:
                winreg.SetValueEx(k, "Icon", 0, winreg.REG_SZ, icon)
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, base + r"\command") as k:
            winreg.SetValueEx(k, "", 0, winreg.REG_SZ, cmd)


def unregister_combine() -> None:
    """Remove registry entries for the combine multi-select context menu."""
    import winreg
    for ext in COMBINE_EXTENSIONS:
        base = rf"Software\Classes\SystemFileAssociations\{ext}\shell\{_COMBINE_VERB}"
        for sub in (r"\command", ""):
            try:
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, base + sub)
            except FileNotFoundError:
                pass


def is_combine_registered() -> bool:
    """Return True if the combine context menu is currently registered."""
    import winreg
    try:
        key = rf"Software\Classes\SystemFileAssociations\.pdf\shell\{_COMBINE_VERB}"
        winreg.OpenKey(winreg.HKEY_CURRENT_USER, key).Close()
        return True
    except FileNotFoundError:
        return False
