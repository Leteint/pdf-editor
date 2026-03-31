"""
Dialog for adding a predefined rubber stamp to PDF pages.
"""
from __future__ import annotations
import math

from PySide6.QtWidgets import (
    QDialog, QHBoxLayout, QVBoxLayout, QFormLayout,
    QComboBox, QSlider, QLabel, QLineEdit,
    QDialogButtonBox, QSizePolicy,
)
from PySide6.QtGui import QPainter, QColor, QFont, QPen
from PySide6.QtCore import Qt
from utils.i18n import _

# name → (r, g, b)
_STAMPS: dict[str, tuple] = {
    "APPROUVÉ":     (0.05, 0.55, 0.10),
    "REJETÉ":       (0.80, 0.10, 0.10),
    "À SIGNER":     (0.10, 0.20, 0.80),
    "CONFIDENTIEL": (0.80, 0.10, 0.10),
    "BROUILLON":    (0.45, 0.45, 0.45),
    "URGENT":       (0.90, 0.40, 0.00),
    "COPIE":        (0.45, 0.45, 0.45),
    "À RÉVISER":    (0.90, 0.40, 0.00),
}

_POSITIONS = [
    (_("Haut-droit"),   "top-right"),
    (_("Haut-gauche"),  "top-left"),
    (_("Bas-droit"),    "bottom-right"),
    (_("Bas-gauche"),   "bottom-left"),
    (_("Centre"),       "center"),
]

_PAGES = [
    (_("Toutes les pages"), "all"),
    (_("Première page"),    "first"),
    (_("Dernière page"),    "last"),
]


# ---------------------------------------------------------------------------
# Preview widget
# ---------------------------------------------------------------------------

class _StampPreview(QLabel):
    """Small A4-like preview that renders the stamp via QPainter."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setFixedSize(150, 210)
        self.setStyleSheet("background: #f0f0f0; border: 1px solid #ccc;")
        self._text     = "APPROUVÉ"
        self._color    = (0.05, 0.55, 0.10)
        self._position = "top-right"
        self._rotation = 0
        self._opacity  = 0.80

    def refresh(self, text: str, color: tuple, position: str,
                rotation: int, opacity: float) -> None:
        self._text     = text or "?"
        self._color    = color
        self._position = position
        self._rotation = rotation
        self._opacity  = opacity
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        super().paintEvent(event)
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        W, H = self.width(), self.height()
        mg = 8                          # widget margin
        pw, ph = W - 2 * mg, H - 2 * mg

        # --- page background ---
        p.fillRect(mg, mg, pw, ph, QColor(255, 255, 255))
        p.setPen(QColor(180, 180, 180))
        p.drawRect(mg, mg, pw, ph)

        # --- fake text lines ---
        p.setPen(QColor(215, 215, 215))
        for i in range(7):
            y = mg + 20 + i * 16
            p.drawLine(mg + 8, y, mg + pw - 8, y)

        # --- stamp ---
        r, g, b = self._color
        qcolor = QColor(int(r * 255), int(g * 255), int(b * 255))

        font = QFont("Arial", 8, QFont.Weight.Bold)
        p.setFont(font)
        fm   = p.fontMetrics()
        tw   = fm.horizontalAdvance(self._text)
        th   = fm.height()
        pad  = 5
        bw   = tw + 2 * pad
        bh   = th + 2 * pad

        em = 12  # edge margin inside page
        if self._position == "top-right":
            cx = mg + pw - em - bw / 2
            cy = mg + em + bh / 2
        elif self._position == "top-left":
            cx = mg + em + bw / 2
            cy = mg + em + bh / 2
        elif self._position == "bottom-right":
            cx = mg + pw - em - bw / 2
            cy = mg + ph - em - bh / 2
        elif self._position == "bottom-left":
            cx = mg + em + bw / 2
            cy = mg + ph - em - bh / 2
        else:
            cx = mg + pw / 2
            cy = mg + ph / 2

        p.save()
        p.translate(cx, cy)
        if self._rotation != 0:
            p.rotate(self._rotation)
        p.setOpacity(self._opacity)

        # light fill
        fill = QColor(int(r * 255), int(g * 255), int(b * 255), 30)
        p.fillRect(int(-bw / 2), int(-bh / 2), int(bw), int(bh), fill)

        # border (double-line effect: outer thick, inner thinner)
        outer_pen = QPen(qcolor, 2)
        p.setPen(outer_pen)
        p.drawRect(int(-bw / 2), int(-bh / 2), int(bw), int(bh))

        # text
        p.setPen(qcolor)
        p.drawText(
            int(-bw / 2), int(-bh / 2), int(bw), int(bh),
            Qt.AlignmentFlag.AlignCenter,
            self._text,
        )
        p.restore()
        p.end()


# ---------------------------------------------------------------------------
# Dialog
# ---------------------------------------------------------------------------

class StampDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(_("Ajouter un tampon"))
        self.setMinimumWidth(500)
        self._build()
        self._refresh_preview()

    def _build(self) -> None:
        root = QHBoxLayout(self)

        # ── Left: controls ──────────────────────────────────────────────
        left = QVBoxLayout()
        form = QFormLayout()
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        # Stamp selection
        self._stamp_combo = QComboBox()
        for name in _STAMPS:
            self._stamp_combo.addItem(_(name), name)
        self._stamp_combo.addItem(_("Personnalisé…"), "__custom__")
        form.addRow(_("Tampon :"), self._stamp_combo)

        # Custom text (hidden by default)
        self._custom_edit = QLineEdit()
        self._custom_edit.setPlaceholderText(_("Votre texte…"))
        self._custom_edit.setVisible(False)
        form.addRow("", self._custom_edit)

        # Position
        self._pos_combo = QComboBox()
        for label, val in _POSITIONS:
            self._pos_combo.addItem(label, val)
        form.addRow(_("Position :"), self._pos_combo)

        # Pages
        self._pages_combo = QComboBox()
        for label, val in _PAGES:
            self._pages_combo.addItem(label, val)
        form.addRow(_("Pages :"), self._pages_combo)

        # Rotation
        self._rot_combo = QComboBox()
        self._rot_combo.addItem(_("Horizontal  (0°)"),   0)
        self._rot_combo.addItem(_("Diagonal  (−45°)"), -45)
        form.addRow(_("Rotation :"), self._rot_combo)

        # Opacity
        opacity_row = QHBoxLayout()
        self._opacity = QSlider(Qt.Orientation.Horizontal)
        self._opacity.setRange(10, 100)
        self._opacity.setValue(80)
        self._opacity_lbl = QLabel("80 %")
        self._opacity_lbl.setFixedWidth(38)
        self._opacity.valueChanged.connect(
            lambda v: self._opacity_lbl.setText(f"{v} %")
        )
        opacity_row.addWidget(self._opacity)
        opacity_row.addWidget(self._opacity_lbl)
        form.addRow(_("Opacité :"), opacity_row)

        left.addLayout(form)
        left.addStretch()

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        btns.button(QDialogButtonBox.StandardButton.Ok).setText(_("Appliquer"))
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        left.addWidget(btns)

        root.addLayout(left, stretch=3)

        # ── Right: preview ───────────────────────────────────────────────
        right = QVBoxLayout()
        lbl = QLabel(_("Aperçu :"))
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right.addWidget(lbl)
        self._preview = _StampPreview()
        self._preview.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        right.addWidget(self._preview, alignment=Qt.AlignmentFlag.AlignCenter)
        right.addStretch()
        root.addLayout(right, stretch=2)

        # ── Connect signals ──────────────────────────────────────────────
        self._stamp_combo.currentIndexChanged.connect(self._on_stamp_changed)
        self._custom_edit.textChanged.connect(self._refresh_preview)
        self._pos_combo.currentIndexChanged.connect(self._refresh_preview)
        self._rot_combo.currentIndexChanged.connect(self._refresh_preview)
        self._opacity.valueChanged.connect(self._refresh_preview)

    # ------------------------------------------------------------------

    def _on_stamp_changed(self, _idx: int) -> None:
        is_custom = self._stamp_combo.currentData() == "__custom__"
        self._custom_edit.setVisible(is_custom)
        self._refresh_preview()

    def _refresh_preview(self, *_args) -> None:
        self._preview.refresh(
            self.stamp_text,
            self.color,
            self._pos_combo.currentData(),
            self._rot_combo.currentData(),
            self._opacity.value() / 100.0,
        )

    # ------------------------------------------------------------------
    # Result properties
    # ------------------------------------------------------------------

    @property
    def stamp_text(self) -> str:
        key = self._stamp_combo.currentData()
        if key == "__custom__":
            return self._custom_edit.text().strip() or "TAMPON"
        return key

    @property
    def color(self) -> tuple:
        key = self._stamp_combo.currentData()
        return _STAMPS.get(key, (0.5, 0.5, 0.5))

    @property
    def position(self) -> str:
        return self._pos_combo.currentData()

    @property
    def pages(self) -> str:
        return self._pages_combo.currentData()

    @property
    def rotation(self) -> int:
        return self._rot_combo.currentData()

    @property
    def opacity(self) -> float:
        return self._opacity.value() / 100.0
