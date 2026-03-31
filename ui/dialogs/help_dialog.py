"""
Fenêtre d'aide — affiche le Manuel utilisateur (Markdown → HTML).
Accessible via F1 ou menu Aide → Manuel utilisateur.
"""
from __future__ import annotations

import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextBrowser,
    QPushButton, QLineEdit, QLabel,
)
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtCore import Qt

from utils.i18n import _

# Chemin vers le fichier Markdown.
# En mode PyInstaller le bundle est dans sys._MEIPASS ; en dev c'est la racine.
import sys as _sys
_BASE = getattr(_sys, "_MEIPASS", None) or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", ".."
)

def _resolve_md_path() -> str:
    """Retourne le chemin du manuel dans la langue active, avec fallback FR."""
    from utils.i18n import get_language
    lang = get_language()  # "fr", "en", "es", "it", "de", "pt"…
    path = os.path.join(_BASE, "docs", f"Manuel_utilisateur_{lang}.md")
    if not os.path.isfile(path):
        path = os.path.join(_BASE, "docs", "Manuel_utilisateur_fr.md")
    return path


def _md_to_html(md_text: str) -> str:
    """Convertit le Markdown en HTML avec une feuille de style intégrée."""
    try:
        import markdown
        body = markdown.markdown(
            md_text,
            extensions=["tables", "fenced_code", "toc"],
        )
    except Exception:
        # Fallback minimaliste si le module n'est pas disponible
        body = "<pre>" + md_text.replace("<", "&lt;") + "</pre>"

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body       {{ font-family: Segoe UI, Arial, sans-serif; font-size: 13px;
                margin: 16px 24px; line-height: 1.6; }}
  h1         {{ font-size: 20px; border-bottom: 2px solid #555; padding-bottom: 6px; }}
  h2         {{ font-size: 16px; border-bottom: 1px solid #444; padding-bottom: 4px;
                margin-top: 28px; }}
  h3         {{ font-size: 14px; margin-top: 18px; }}
  table      {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
  th, td     {{ border: 1px solid #555; padding: 5px 10px; text-align: left; }}
  th         {{ background: #3a3a3a; }}
  tr:nth-child(even) {{ background: #2d2d2d; }}
  code, tt   {{ background: #2a2a2a; padding: 1px 4px; border-radius: 3px;
                font-family: Consolas, monospace; font-size: 12px; }}
  pre        {{ background: #1e1e1e; padding: 10px; border-radius: 4px;
                overflow-x: auto; }}
  blockquote {{ border-left: 3px solid #888; padding-left: 12px; color: #aaa; }}
  a          {{ color: #6aacff; }}
  hr         {{ border: none; border-top: 1px solid #444; margin: 20px 0; }}
</style>
</head>
<body>
{body}
</body>
</html>"""


class HelpDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(_("Manuel utilisateur — PDF Editor"))
        self.resize(820, 680)
        self._build()
        self._load_content()

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(6)

        # ── Barre de recherche ──────────────────────────────────────────
        search_row = QHBoxLayout()
        search_row.addWidget(QLabel(_("Rechercher :")))
        self._search = QLineEdit()
        self._search.setPlaceholderText(_("Mot-clé…"))
        self._search.returnPressed.connect(self._find_next)
        search_row.addWidget(self._search)
        btn_prev = QPushButton("▲")
        btn_prev.setFixedWidth(30)
        btn_prev.setToolTip(_("Occurrence précédente"))
        btn_prev.clicked.connect(self._find_prev)
        btn_next = QPushButton("▼")
        btn_next.setFixedWidth(30)
        btn_next.setToolTip(_("Occurrence suivante"))
        btn_next.clicked.connect(self._find_next)
        search_row.addWidget(btn_prev)
        search_row.addWidget(btn_next)
        layout.addLayout(search_row)

        # ── Navigateur ─────────────────────────────────────────────────
        self._browser = QTextBrowser()
        self._browser.setOpenExternalLinks(True)
        layout.addWidget(self._browser)

        # ── Bouton Fermer ───────────────────────────────────────────────
        close_btn = QPushButton(_("Fermer"))
        close_btn.setFixedWidth(100)
        close_btn.clicked.connect(self.accept)
        bottom = QHBoxLayout()
        bottom.addStretch()
        bottom.addWidget(close_btn)
        layout.addLayout(bottom)

        # Raccourci Échap pour fermer
        QShortcut(QKeySequence("Escape"), self, self.accept)

    def _load_content(self) -> None:
        path = os.path.normpath(_resolve_md_path())
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as fh:
                md_text = fh.read()
            self._browser.setHtml(_md_to_html(md_text))
        else:
            self._browser.setPlainText(
                _("Fichier de documentation introuvable :\n") + path
            )

    # ── Recherche dans le texte ─────────────────────────────────────────
    def _find_next(self) -> None:
        from PySide6.QtGui import QTextDocument
        term = self._search.text()
        if term:
            found = self._browser.find(term)
            if not found:
                # Revenir au début et réessayer
                cursor = self._browser.textCursor()
                cursor.movePosition(cursor.MoveOperation.Start)
                self._browser.setTextCursor(cursor)
                self._browser.find(term)

    def _find_prev(self) -> None:
        from PySide6.QtGui import QTextDocument
        term = self._search.text()
        if term:
            from PySide6.QtGui import QTextDocument
            self._browser.find(
                term,
                QTextDocument.FindFlag.FindBackward,
            )
