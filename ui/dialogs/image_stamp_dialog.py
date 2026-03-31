"""
Dialog for applying a custom image stamp (logo, signature…) to PDF pages.
The stamp library is persisted across sessions via StampStore.
"""
from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog, QHBoxLayout, QVBoxLayout, QFormLayout,
    QListWidget, QListWidgetItem, QPushButton, QLabel,
    QComboBox, QSlider, QSpinBox, QDialogButtonBox,
    QFileDialog, QInputDialog, QMessageBox, QSizePolicy,
)
from PySide6.QtGui import QPixmap, QIcon, QPainter, QColor
from PySide6.QtCore import Qt, QSize
from utils.i18n import _
from utils.stamp_store import StampStore

_POSITIONS = [
    (_("Bas-droit"),    "bottom-right"),
    (_("Bas-gauche"),   "bottom-left"),
    (_("Haut-droit"),   "top-right"),
    (_("Haut-gauche"),  "top-left"),
    (_("Centre"),       "center"),
]

_PAGES = [
    (_("Toutes les pages"), "all"),
    (_("Première page"),    "first"),
    (_("Dernière page"),    "last"),
]


# ---------------------------------------------------------------------------
# Stamp preview
# ---------------------------------------------------------------------------

class _StampPreview(QLabel):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setFixedSize(150, 210)
        self.setStyleSheet("background: #f0f0f0; border: 1px solid #ccc;")
        self._pixmap:  QPixmap | None = None
        self._position = "bottom-right"
        self._scale    = 25
        self._opacity  = 1.0

    def refresh(self, pixmap: QPixmap | None, position: str,
                scale: int, opacity: float) -> None:
        self._pixmap   = pixmap
        self._position = position
        self._scale    = scale
        self._opacity  = opacity
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        super().paintEvent(event)
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        W, H = self.width(), self.height()
        mg = 8
        pw, ph = W - 2 * mg, H - 2 * mg

        # Page background
        p.fillRect(mg, mg, pw, ph, QColor(255, 255, 255))
        p.setPen(QColor(180, 180, 180))
        p.drawRect(mg, mg, pw, ph)

        # Fake content lines
        p.setPen(QColor(215, 215, 215))
        for i in range(7):
            y = mg + 20 + i * 16
            p.drawLine(mg + 8, y, mg + pw - 8, y)

        if self._pixmap and not self._pixmap.isNull():
            sw = int(pw * self._scale / 100)
            sh = int(sw * self._pixmap.height() / max(self._pixmap.width(), 1))
            em = 8

            if self._position == "bottom-right":
                sx, sy = mg + pw - em - sw, mg + ph - em - sh
            elif self._position == "bottom-left":
                sx, sy = mg + em, mg + ph - em - sh
            elif self._position == "top-right":
                sx, sy = mg + pw - em - sw, mg + em
            elif self._position == "top-left":
                sx, sy = mg + em, mg + em
            else:  # center
                sx, sy = mg + (pw - sw) // 2, mg + (ph - sh) // 2

            p.setOpacity(self._opacity)
            scaled = self._pixmap.scaled(
                sw, sh,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            p.drawPixmap(sx, sy, scaled)

        p.end()


# ---------------------------------------------------------------------------
# Dialog
# ---------------------------------------------------------------------------

class ImageStampDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(_("Tampon image"))
        self.setMinimumSize(620, 400)
        self._store = StampStore()
        self._build()
        self._reload_list()

    # ------------------------------------------------------------------
    # Build UI
    # ------------------------------------------------------------------

    def _build(self) -> None:
        root = QHBoxLayout(self)

        # ── Left: stamp library ─────────────────────────────────────────
        left = QVBoxLayout()
        left.addWidget(QLabel(_("Bibliothèque de tampons :")))

        self._list = QListWidget()
        self._list.setIconSize(QSize(64, 64))
        self._list.setFixedWidth(200)
        self._list.currentRowChanged.connect(self._on_selection)
        left.addWidget(self._list, stretch=1)

        lib_btns = QHBoxLayout()
        self._btn_add = QPushButton("➕ " + _("Ajouter…"))
        self._btn_del = QPushButton("🗑")
        self._btn_del.setFixedWidth(36)
        self._btn_del.setStyleSheet("color: #e55;")
        self._btn_del.setToolTip(_("Supprimer ce tampon de la bibliothèque"))
        lib_btns.addWidget(self._btn_add)
        lib_btns.addWidget(self._btn_del)
        left.addLayout(lib_btns)

        root.addLayout(left)

        # ── Middle: options ──────────────────────────────────────────────
        mid = QVBoxLayout()
        form = QFormLayout()
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        self._pos_combo = QComboBox()
        for label, val in _POSITIONS:
            self._pos_combo.addItem(label, val)
        form.addRow(_("Position :"), self._pos_combo)

        self._pages_combo = QComboBox()
        for label, val in _PAGES:
            self._pages_combo.addItem(label, val)
        form.addRow(_("Pages :"), self._pages_combo)

        self._scale_spin = QSpinBox()
        self._scale_spin.setRange(5, 100)
        self._scale_spin.setValue(25)
        self._scale_spin.setSuffix(_(" % largeur page"))
        form.addRow(_("Taille :"), self._scale_spin)

        opacity_row = QHBoxLayout()
        self._opacity = QSlider(Qt.Orientation.Horizontal)
        self._opacity.setRange(10, 100)
        self._opacity.setValue(100)
        self._opacity_lbl = QLabel("100 %")
        self._opacity_lbl.setFixedWidth(38)
        self._opacity.valueChanged.connect(
            lambda v: self._opacity_lbl.setText(f"{v} %")
        )
        opacity_row.addWidget(self._opacity)
        opacity_row.addWidget(self._opacity_lbl)
        form.addRow(_("Opacité :"), opacity_row)

        mid.addLayout(form)
        mid.addStretch()

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        btns.button(QDialogButtonBox.StandardButton.Ok).setText(_("Appliquer"))
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        mid.addWidget(btns)

        root.addLayout(mid, stretch=2)

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
        root.addLayout(right, stretch=1)

        # ── Connect signals ──────────────────────────────────────────────
        self._btn_add.clicked.connect(self._add_stamp)
        self._btn_del.clicked.connect(self._delete_stamp)
        self._pos_combo.currentIndexChanged.connect(self._refresh_preview)
        self._scale_spin.valueChanged.connect(self._refresh_preview)
        self._opacity.valueChanged.connect(self._refresh_preview)

    # ------------------------------------------------------------------
    # Library management
    # ------------------------------------------------------------------

    def _reload_list(self) -> None:
        self._list.clear()
        for entry in self._store.stamps:
            path = self._store.full_path(entry)
            pm   = QPixmap(path).scaled(
                64, 64,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            item = QListWidgetItem(QIcon(pm), entry["name"])
            self._list.addItem(item)
        if self._list.count():
            self._list.setCurrentRow(0)
        self._refresh_apply_btn()

    def _add_stamp(self) -> None:
        path, _filt = QFileDialog.getOpenFileName(
            self, _("Choisir une image"),
            "",
            _("Images (*.png *.jpg *.jpeg *.bmp *.webp *.tiff *.tif)"),
        )
        if not path:
            return
        name, ok = QInputDialog.getText(
            self, _("Nom du tampon"),
            _("Donnez un nom à ce tampon :"),
            text=_("Mon tampon"),
        )
        if not ok or not name.strip():
            return
        self._store.add(path, name.strip())
        self._reload_list()
        self._list.setCurrentRow(self._list.count() - 1)

    def _delete_stamp(self) -> None:
        row = self._list.currentRow()
        if row < 0:
            return
        name = self._store.stamps[row]["name"]
        if QMessageBox.question(
            self, _("Supprimer"),
            _("Supprimer le tampon « {n} » de la bibliothèque ?").format(n=name),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        ) != QMessageBox.StandardButton.Yes:
            return
        self._store.remove(row)
        self._reload_list()

    # ------------------------------------------------------------------
    # Preview
    # ------------------------------------------------------------------

    def _on_selection(self, row: int) -> None:
        # Load defaults from stored entry
        stamps = self._store.stamps
        if 0 <= row < len(stamps):
            entry = stamps[row]
            for i in range(self._pos_combo.count()):
                if self._pos_combo.itemData(i) == entry.get("position", "bottom-right"):
                    self._pos_combo.setCurrentIndex(i)
                    break
            self._scale_spin.setValue(entry.get("scale_pct", 25))
            self._opacity.setValue(int(entry.get("opacity", 1.0) * 100))
        self._refresh_preview()
        self._refresh_apply_btn()

    def _refresh_preview(self, *_args) -> None:
        row = self._list.currentRow()
        stamps = self._store.stamps
        if 0 <= row < len(stamps):
            pm = QPixmap(self._store.full_path(stamps[row]))
        else:
            pm = None
        self._preview.refresh(
            pm,
            self._pos_combo.currentData(),
            self._scale_spin.value(),
            self._opacity.value() / 100.0,
        )

    def _refresh_apply_btn(self) -> None:
        btns = self.findChild(QDialogButtonBox)
        if btns:
            ok = btns.button(QDialogButtonBox.StandardButton.Ok)
            if ok:
                ok.setEnabled(self._list.currentRow() >= 0)

    # ------------------------------------------------------------------
    # Result properties
    # ------------------------------------------------------------------

    @property
    def selected_image_path(self) -> str:
        row = self._list.currentRow()
        stamps = self._store.stamps
        if 0 <= row < len(stamps):
            return self._store.full_path(stamps[row])
        return ""

    @property
    def position(self) -> str:
        return self._pos_combo.currentData()

    @property
    def pages(self) -> str:
        return self._pages_combo.currentData()

    @property
    def scale_pct(self) -> int:
        return self._scale_spin.value()

    @property
    def opacity(self) -> float:
        return self._opacity.value() / 100.0
