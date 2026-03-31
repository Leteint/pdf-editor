"""Left-panel tab — language selection."""
from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QButtonGroup, QRadioButton,
    QLabel, QFrame, QPushButton, QSizePolicy,
)
from utils.i18n import _, SUPPORTED_LANGUAGES, get_language

_FLAGS: dict[str, str] = {
    "fr": "🇫🇷",
    "en": "🇬🇧",
    "de": "🇩🇪",
    "es": "🇪🇸",
    "it": "🇮🇹",
    "pt": "🇵🇹",
    "ru": "🇷🇺",
}


class LanguagePanel(QWidget):
    """Simple language selector panel."""

    language_selected = Signal(str)   # lang code

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._build()

    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 10, 8, 8)
        root.setSpacing(4)

        lbl = QLabel(_("Choisir la langue :"))
        lbl.setStyleSheet("font-weight: bold; color: #ccc; padding-bottom: 4px;")
        root.addWidget(lbl)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #555; margin-bottom: 6px;")
        root.addWidget(sep)

        self._group = QButtonGroup(self)
        current = get_language()

        for code, display_name in SUPPORTED_LANGUAGES.items():
            flag = _FLAGS.get(code, "")
            rb = QRadioButton(f"{flag}  {display_name}")
            rb.setChecked(code == current)
            rb.setStyleSheet(
                "QRadioButton { padding: 5px 4px; font-size: 13px; }"
                "QRadioButton:hover { color: #4a90d9; }"
                "QRadioButton:checked { color: #4a90d9; font-weight: bold; }"
            )
            rb.toggled.connect(
                lambda checked, c=code: self.language_selected.emit(c) if checked else None
            )
            self._group.addButton(rb)
            root.addWidget(rb)

        root.addSpacing(12)

        note = QLabel(_("Un redémarrage est nécessaire\npour appliquer le changement."))
        note.setStyleSheet("color: #888; font-size: 11px;")
        note.setWordWrap(True)
        root.addWidget(note)

        root.addStretch()
