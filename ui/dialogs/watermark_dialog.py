"""
Dialog for adding a text watermark to all pages.
"""
from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog, QFormLayout, QVBoxLayout, QHBoxLayout,
    QLineEdit, QSpinBox, QSlider, QLabel, QComboBox,
    QDialogButtonBox,
)
from PySide6.QtCore import Qt
from utils.i18n import _

_COLORS = {
    "Gris":     (0.6, 0.6, 0.6),
    "Rouge":    (0.8, 0.1, 0.1),
    "Bleu":     (0.1, 0.2, 0.8),
    "Vert":     (0.1, 0.6, 0.1),
    "Noir":     (0.0, 0.0, 0.0),
}


class WatermarkDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(_("Ajouter un filigrane"))
        self.setMinimumWidth(380)
        self._build()

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        form   = QFormLayout()

        # Text
        self._text = QLineEdit("CONFIDENTIEL")
        form.addRow(_("Texte :"), self._text)

        # Font size
        self._size = QSpinBox()
        self._size.setRange(10, 150)
        self._size.setValue(60)
        self._size.setSuffix(" pt")
        form.addRow(_("Taille :"), self._size)

        # Color
        self._color = QComboBox()
        for name in _COLORS:
            self._color.addItem(_(name), _COLORS[name])
        form.addRow(_("Couleur :"), self._color)

        # Opacity
        opacity_row = QHBoxLayout()
        self._opacity = QSlider(Qt.Orientation.Horizontal)
        self._opacity.setRange(5, 100)
        self._opacity.setValue(25)
        self._opacity_lbl = QLabel("25 %")
        self._opacity.valueChanged.connect(
            lambda v: self._opacity_lbl.setText(f"{v} %")
        )
        opacity_row.addWidget(self._opacity)
        opacity_row.addWidget(self._opacity_lbl)
        form.addRow(_("Opacité :"), opacity_row)

        layout.addLayout(form)

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        btns.button(QDialogButtonBox.StandardButton.Ok).setText(_("Appliquer"))
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    @property
    def watermark_text(self) -> str:
        return self._text.text().strip() or "FILIGRANE"

    @property
    def font_size(self) -> int:
        return self._size.value()

    @property
    def color(self) -> tuple:
        return self._color.currentData()

    @property
    def opacity(self) -> float:
        return self._opacity.value() / 100.0
