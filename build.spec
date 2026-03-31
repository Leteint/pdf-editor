# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file
#
# Usage:
#   pyinstaller build.spec
#
# Or use build_installer.bat which runs everything automatically.
#
# Environment variables (optional):
#   TESSERACT_DIR  — path to Tesseract-OCR installation
#                    (default: C:\Program Files\Tesseract-OCR)

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, collect_dynamic_libs

# ---------------------------------------------------------------------------
# Data files
# ---------------------------------------------------------------------------
datas = [
    ('assets',  'assets'),   # themes, translations, icons …
    ('docs',    'docs'),     # manuel utilisateur
]

# pypdfium2 ships prebuilt native binaries that must be collected
try:
    datas += collect_data_files('pypdfium2', include_py_files=False)
except Exception:
    pass

try:
    datas += collect_data_files('pikepdf')
except Exception:
    pass

try:
    datas += collect_data_files('pdfplumber')
except Exception:
    pass

# pyhanko ships certificate stores as data files
try:
    datas += collect_data_files('pyhanko')
except Exception:
    pass

try:
    datas += collect_data_files('pyhanko_certvalidator')
except Exception:
    pass

# certifi CA bundle (used by several packages)
try:
    datas += collect_data_files('certifi')
except Exception:
    pass

# ---------------------------------------------------------------------------
# Optional: bundle Tesseract-OCR (large — ~80 MB with eng+fra)
# Set TESSERACT_DIR to the installation folder, or leave empty to skip.
# If omitted the app still works; the user just needs Tesseract installed.
# ---------------------------------------------------------------------------
tesseract_dir = os.environ.get(
    'TESSERACT_DIR',
    r'C:\Program Files\Tesseract-OCR',
)
BUNDLE_TESSERACT = os.path.isdir(tesseract_dir)
if BUNDLE_TESSERACT:
    datas += [(tesseract_dir, 'tesseract')]
    print(f"[build.spec] Bundling Tesseract from: {tesseract_dir}")
else:
    print("[build.spec] Tesseract NOT bundled (set TESSERACT_DIR to include it).")

# ---------------------------------------------------------------------------
# Hidden imports
# ---------------------------------------------------------------------------
hidden_imports = (
    collect_submodules('pikepdf') +
    collect_submodules('pdfplumber') +
    collect_submodules('pypdf') +
    collect_submodules('pyhanko') +
    collect_submodules('pyhanko_certvalidator') +
    [
        'pytesseract',
        'PIL',
        'PIL.Image',
        'PIL.ImageFilter',
        'PIL.ImageEnhance',
        # PySide6 plugins loaded at runtime
        'PySide6.QtSvg',
        'PySide6.QtPrintSupport',
        # assets.translations — ensure the package is found at runtime
        'assets',
        'assets.translations',
        'assets.translations.en',
        'assets.translations.es',
        'assets.translations.it',
        'assets.translations.ru',
    ]
)

# ---------------------------------------------------------------------------
# Binaries — collect dynamic libs that PyInstaller might miss
# ---------------------------------------------------------------------------
binaries = []
try:
    binaries += collect_dynamic_libs('pypdfium2')
except Exception:
    pass

# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------
a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=['hooks'],      # local hooks/ folder (see below)
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',            # not used
        'matplotlib',
        'scipy',
        'numpy',              # only needed if a dep explicitly requires it
        'IPython',
        'jupyter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,       # onefile: embed binaries directly
    a.zipfiles,
    a.datas,          # onefile: embed data files directly
    [],
    name='PDFEditor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,        # UPX disabled — causes crashes with PySide6
    console=False,    # no console window
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icons/icon.ico',
    # onefile mode: everything packed into a single PDFEditor.exe
)
