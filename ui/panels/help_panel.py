"""Left-panel tab — help & shortcuts."""
from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame, QPushButton, QScrollArea,
)
from utils.i18n import _


_SHORTCUTS = [
    ("Ctrl+O",       "Ouvrir un PDF"),
    ("Ctrl+S",       "Enregistrer"),
    ("Ctrl+Shift+S", "Enregistrer sous…"),
    ("Ctrl+Z",       "Annuler"),
    ("Ctrl+Y",       "Rétablir"),
    ("Ctrl+F",       "Rechercher…"),
    ("F1",           "Manuel utilisateur"),
    ("Delete",       "Supprimer la page"),
    ("H",            "Outil Surligner"),
    ("C",            "Outil Commentaire"),
    ("E",            "Outil Effacer"),
    ("M",            "Déplacer texte"),
]


class HelpPanel(QWidget):
    """Help & shortcuts panel."""

    open_manual_requested     = Signal()
    open_shell_int_requested  = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._build()

    def _build(self) -> None:
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        root = QVBoxLayout(container)
        root.setContentsMargins(8, 10, 8, 8)
        root.setSpacing(4)

        # ── Actions rapides ────────────────────────────────────────────────
        lbl_actions = QLabel(_("Actions rapides :"))
        lbl_actions.setStyleSheet("font-weight: bold; color: #ccc; padding-bottom: 4px;")
        root.addWidget(lbl_actions)

        sep1 = QFrame()
        sep1.setFrameShape(QFrame.Shape.HLine)
        sep1.setStyleSheet("color: #555; margin-bottom: 4px;")
        root.addWidget(sep1)

        btn_manual = QPushButton("📖  " + _("Manuel utilisateur") + "  [F1]")
        btn_manual.setStyleSheet(
            "QPushButton { padding: 7px 8px; text-align: left; border-radius: 3px; }"
            "QPushButton:hover { background: #4a90d9; color: white; }"
        )
        btn_manual.clicked.connect(self.open_manual_requested.emit)
        root.addWidget(btn_manual)

        btn_shell = QPushButton("🖥  " + _("Intégration Windows (clic droit)…"))
        btn_shell.setStyleSheet(
            "QPushButton { padding: 7px 8px; text-align: left; border-radius: 3px; }"
            "QPushButton:hover { background: #555; }"
        )
        btn_shell.clicked.connect(self.open_shell_int_requested.emit)
        root.addWidget(btn_shell)

        root.addSpacing(10)

        # ── Raccourcis clavier ─────────────────────────────────────────────
        lbl_sc = QLabel(_("Raccourcis clavier :"))
        lbl_sc.setStyleSheet("font-weight: bold; color: #ccc; padding-bottom: 4px;")
        root.addWidget(lbl_sc)

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet("color: #555; margin-bottom: 4px;")
        root.addWidget(sep2)

        for key, desc in _SHORTCUTS:
            row = QWidget()
            rl = QVBoxLayout(row)
            rl.setContentsMargins(0, 0, 0, 0)
            rl.setSpacing(0)

            lbl = QLabel(f"<b style='color:#4a90d9'>{key}</b>"
                         f"<span style='color:#aaa'>  {_(desc)}</span>")
            lbl.setStyleSheet("font-size: 11px; padding: 2px 4px;")
            rl.addWidget(lbl)
            root.addWidget(row)

        root.addStretch()
        scroll.setWidget(container)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)
