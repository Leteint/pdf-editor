"""
Dialog for adding headers and footers to all pages.
Supports left/centre/right zones and {page}, {total}, {date} tokens.
"""
from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLineEdit, QSpinBox, QCheckBox, QLabel, QPushButton,
    QDialogButtonBox, QComboBox, QGridLayout,
)
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt
from utils.i18n import _

_COLORS = {
    "Noir":     (0.0, 0.0, 0.0),
    "Gris":     (0.4, 0.4, 0.4),
    "Rouge":    (0.8, 0.1, 0.1),
    "Bleu":     (0.1, 0.2, 0.8),
}


class HeaderFooterDialog(QDialog):
    def __init__(self, page_count: int, parent=None, initial: dict | None = None) -> None:
        super().__init__(parent)
        self._page_count = page_count
        self.setWindowTitle(_("En-têtes et pieds de page"))
        self.setMinimumWidth(520)
        self._build()
        if initial:
            self._apply_initial(initial)

    def _apply_initial(self, d: dict) -> None:
        """Pre-populate fields from a previously saved settings dict."""
        hl, hc, hr = d.get("header", ("", "", ""))
        self._hdr["left"].setText(hl)
        self._hdr["center"].setText(hc)
        self._hdr["right"].setText(hr)

        fl, fc, fr = d.get("footer", ("", "", ""))
        self._ftr["left"].setText(fl)
        self._ftr["center"].setText(fc)
        self._ftr["right"].setText(fr)

        if "font_size" in d:
            self._font_size.setValue(d["font_size"])
        if "margin_mm" in d:
            self._margin.setValue(d["margin_mm"])
        if "skip_first" in d:
            self._skip_first.setChecked(d["skip_first"])
        if "color" in d:
            for i in range(self._color.count()):
                if self._color.itemData(i) == d["color"]:
                    self._color.setCurrentIndex(i)
                    break

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # ── Tokens hint ─────────────────────────────────────────────────
        hint = QLabel(
            _("<small>Tokens disponibles : "
              "<b>{page}</b> = numéro de page &nbsp;·&nbsp; "
              "<b>{total}</b> = nombre total &nbsp;·&nbsp; "
              "<b>{date}</b> = date du jour</small>")
        )
        hint.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(hint)

        # ── Header ──────────────────────────────────────────────────────
        self._hdr = self._zone_group(_("En-tête"), "header")
        layout.addWidget(self._hdr["group"])

        # ── Footer ──────────────────────────────────────────────────────
        self._ftr = self._zone_group(_("Pied de page"), "footer")
        layout.addWidget(self._ftr["group"])

        # ── Common options ───────────────────────────────────────────────
        opt_box = QGroupBox(_("Options communes"))
        opt_layout = QFormLayout(opt_box)

        self._font_size = QSpinBox()
        self._font_size.setRange(6, 36)
        self._font_size.setValue(10)
        self._font_size.setSuffix(" pt")
        opt_layout.addRow(_("Taille de police :"), self._font_size)

        self._color = QComboBox()
        for name, val in _COLORS.items():
            self._color.addItem(_(name), val)
        opt_layout.addRow(_("Couleur :"), self._color)

        self._margin = QSpinBox()
        self._margin.setRange(3, 50)
        self._margin.setValue(15)
        self._margin.setSuffix(" mm")
        opt_layout.addRow(_("Marge depuis le bord :"), self._margin)

        self._skip_first = QCheckBox(_("Ne pas appliquer sur la 1ère page"))
        opt_layout.addRow("", self._skip_first)

        layout.addWidget(opt_box)

        # ── Buttons ──────────────────────────────────────────────────────
        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        btns.button(QDialogButtonBox.StandardButton.Ok).setText(_("Appliquer"))
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def _zone_group(self, title: str, zone: str) -> dict:
        group = QGroupBox(title)
        grid  = QGridLayout(group)

        grid.addWidget(QLabel(_("Gauche")),  0, 0)
        grid.addWidget(QLabel(_("Centre")),  0, 1)
        grid.addWidget(QLabel(_("Droite")),  0, 2)

        left   = QLineEdit()
        center = QLineEdit()
        right  = QLineEdit()

        # Default: page number centred in footer
        if zone == "footer":
            center.setPlaceholderText("Page {page} / {total}")
        else:
            left.setPlaceholderText(_("En-tête gauche"))

        grid.addWidget(left,   1, 0)
        grid.addWidget(center, 1, 1)
        grid.addWidget(right,  1, 2)

        # Token shortcut buttons
        for col, field in ((0, left), (1, center), (2, right)):
            btn_row = QHBoxLayout()
            for token in ("{page}", "{total}", "{date}"):
                btn = QPushButton(token)
                btn.setFixedHeight(18)
                btn.setStyleSheet("font-size:9px; padding:0 3px;")
                btn.clicked.connect(
                    lambda checked, f=field, t=token: f.insert(t)
                )
                btn_row.addWidget(btn)
            grid.addLayout(btn_row, 2, col)

        return {"group": group, "left": left, "center": center, "right": right}

    # ------------------------------------------------------------------
    # Result properties
    # ------------------------------------------------------------------

    def _zone_texts(self, zone: dict) -> tuple[str, str, str]:
        return (
            zone["left"].text(),
            zone["center"].text(),
            zone["right"].text(),
        )

    @property
    def header(self) -> tuple[str, str, str]:
        return self._zone_texts(self._hdr)

    @property
    def footer(self) -> tuple[str, str, str]:
        return self._zone_texts(self._ftr)

    @property
    def font_size(self) -> int:
        return self._font_size.value()

    @property
    def color(self) -> tuple:
        return self._color.currentData()

    @property
    def margin_mm(self) -> int:
        return self._margin.value()

    @property
    def skip_first(self) -> bool:
        return self._skip_first.isChecked()
