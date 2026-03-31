"""
PDF page viewer widget.
Displays rendered pages and handles mouse interactions for annotations and text editing.
"""
from __future__ import annotations

from typing import Optional
from PySide6.QtCore import Qt, Signal, QPoint, QRect, QRectF, QSize, QEvent
from PySide6.QtGui import (
    QImage, QPainter, QPen, QColor, QCursor, QWheelEvent,
    QMouseEvent, QPaintEvent, QKeyEvent, QFont, QTextCharFormat,
)
from PySide6.QtWidgets import (
    QWidget, QScrollArea, QSizePolicy, QRubberBand, QTextEdit,
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSpinBox, QDoubleSpinBox,
    QFontComboBox, QColorDialog, QApplication, QFrame, QAbstractSpinBox, QCheckBox,
)

from core.renderer import Renderer
from utils.cache import PageCache


# ---------------------------------------------------------------------------
# Mini color button (self-contained, no external dep)
# ---------------------------------------------------------------------------

class _ColorBtn(QPushButton):
    color_changed = Signal(str)

    def __init__(self, color: str = "#000000", parent=None) -> None:
        super().__init__(parent)
        self._color = color
        self.setFixedSize(22, 22)
        self._refresh()
        self.clicked.connect(self._pick)

    def _pick(self) -> None:
        c = QColorDialog.getColor(QColor(self._color), self)
        if c.isValid():
            self._color = c.name()
            self._refresh()
            self.color_changed.emit(self._color)

    def _refresh(self) -> None:
        self.setStyleSheet(
            f"background:{self._color}; border:1px solid #888; border-radius:3px;"
        )

    def set_color(self, c: str) -> None:
        self._color = c
        self._refresh()

    @property
    def color(self) -> str:
        return self._color


# ---------------------------------------------------------------------------
# Live image overlay  (resize-on-drag preview placed over the PDF page)
# ---------------------------------------------------------------------------

class _ImageOverlay(QWidget):
    """
    Floating, resizable image preview shown on the PDF page.
    A compact toolbar at the top lets the user set W/H and confirm or cancel.
    Four corner handles allow freehand resizing by dragging.
    """
    confirmed = Signal(int, int, float, float, float, float)
    # (xobj_w, xobj_h, norm_x, norm_y, norm_w, norm_h) — pixel dims + page-normalised rect
    cancelled = Signal()

    _TB_H   = 40     # toolbar height
    _CORNER = 10     # corner-handle square size
    _MIN    = 40     # minimum image-area size

    _CURSOR_MAP = {
        "tl": Qt.CursorShape.SizeFDiagCursor,
        "tr": Qt.CursorShape.SizeBDiagCursor,
        "bl": Qt.CursorShape.SizeBDiagCursor,
        "br": Qt.CursorShape.SizeFDiagCursor,
    }

    def __init__(self, pil_img, screen_rect: QRect, parent: QWidget) -> None:
        super().__init__(parent)
        self.setMouseTracking(True)
        self._pil_img = pil_img
        sw, sh = screen_rect.width(), screen_rect.height()
        self._ratio = sw / max(sh, 1)
        self._active: Optional[str] = None   # resize handle name
        self._moving: bool = False            # True when dragging to move
        self._drag_start = QPoint()
        self._geom_start = QRect()
        self._qimage: Optional[QImage] = None

        # Place toolbar above the image rect; if no room above, place it below
        tx = screen_rect.x()
        ty = screen_rect.y() - self._TB_H
        if ty < 0:
            ty = screen_rect.y() + screen_rect.height()
        total_w = max(screen_rect.width(), 300)
        total_h = screen_rect.height() + self._TB_H

        self._tb_above = (ty < screen_rect.y() + screen_rect.height())

        self.setGeometry(tx, ty if self._tb_above else screen_rect.y(),
                         total_w, total_h)
        self._build_toolbar()
        self._refresh_image()
        self.show()
        self.raise_()

    # ------------------------------------------------------------------
    # Layout helpers
    # ------------------------------------------------------------------

    def _img_rect(self) -> QRect:
        """Image sub-rect within this widget."""
        if self._tb_above:
            return QRect(0, self._TB_H, self.width(), self.height() - self._TB_H)
        else:
            return QRect(0, 0, self.width(), self.height() - self._TB_H)

    def _corner_rects(self) -> dict:
        c = self._CORNER
        ir = self._img_rect()
        return {
            "tl": QRect(ir.left(),          ir.top(),           c, c),
            "tr": QRect(ir.right() - c,     ir.top(),           c, c),
            "bl": QRect(ir.left(),          ir.bottom() - c,    c, c),
            "br": QRect(ir.right() - c,     ir.bottom() - c,    c, c),
        }

    # ------------------------------------------------------------------
    # Toolbar
    # ------------------------------------------------------------------

    def _build_toolbar(self) -> None:
        tb_y = 0 if self._tb_above else (self.height() - self._TB_H)
        self._tb = QWidget(self)
        self._tb.setGeometry(0, tb_y, self.width(), self._TB_H)
        self._tb.setStyleSheet(
            "QWidget   { background: rgba(25,25,25,230); border-radius:4px; }"
            "QLabel    { color:#ccc; font-size:11px; background:transparent; }"
            "QSpinBox  { background:#fff; color:#111; border:1px solid #888;"
            "            border-radius:3px; padding:1px 3px; font-size:11px; }"
            "QCheckBox { color:#ccc; font-size:11px; background:transparent; }"
        )
        row = QHBoxLayout(self._tb)
        row.setContentsMargins(6, 4, 6, 4)
        row.setSpacing(5)

        row.addWidget(QLabel("L :"))
        self._spin_w = QSpinBox()
        self._spin_w.setRange(self._MIN, 9999)
        self._spin_w.setValue(self._img_rect().width())
        self._spin_w.setSuffix(" px")
        self._spin_w.setFixedWidth(78)
        self._spin_w.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        row.addWidget(self._spin_w)

        row.addWidget(QLabel("H :"))
        self._spin_h = QSpinBox()
        self._spin_h.setRange(self._MIN, 9999)
        self._spin_h.setValue(self._img_rect().height())
        self._spin_h.setSuffix(" px")
        self._spin_h.setFixedWidth(78)
        self._spin_h.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        row.addWidget(self._spin_h)

        self._chk_lock = QCheckBox("=")
        self._chk_lock.setChecked(True)
        self._chk_lock.setToolTip("Conserver le ratio")
        row.addWidget(self._chk_lock)

        row.addStretch()

        btn_ok = QPushButton("✓ Valider")
        btn_ok.setStyleSheet(
            "QPushButton{background:#2e7d32;color:#fff;border:none;border-radius:3px;"
            "padding:2px 8px;font-size:11px;font-weight:bold;}"
            "QPushButton:hover{background:#388e3c;}"
        )
        btn_ok.clicked.connect(self._on_confirm)
        row.addWidget(btn_ok)

        btn_cancel = QPushButton("✗")
        btn_cancel.setStyleSheet(
            "QPushButton{background:#c62828;color:#fff;border:none;border-radius:3px;"
            "padding:2px 8px;font-size:11px;font-weight:bold;}"
            "QPushButton:hover{background:#d32f2f;}"
        )
        btn_cancel.clicked.connect(self._on_cancel)
        row.addWidget(btn_cancel)

        self._spin_w.valueChanged.connect(self._on_spin_w_changed)
        self._spin_h.valueChanged.connect(self._on_spin_h_changed)

    # ------------------------------------------------------------------
    # Image rendering
    # ------------------------------------------------------------------

    def _refresh_image(self) -> None:
        from PIL import Image as PilImage
        ir = self._img_rect()
        w, h = max(1, ir.width()), max(1, ir.height())
        try:
            scaled = self._pil_img.resize((w, h), PilImage.LANCZOS)
            data = scaled.tobytes("raw", "RGB")
            self._qimage = QImage(data, w, h, w * 3, QImage.Format.Format_RGB888)
            self._qimage._data = data
        except Exception:
            self._qimage = None
        self.update()

    # ------------------------------------------------------------------
    # Paint
    # ------------------------------------------------------------------

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        ir = self._img_rect()

        if self._qimage:
            painter.drawImage(ir, self._qimage)
        else:
            painter.fillRect(ir, QColor(200, 200, 200, 80))

        # Dashed border
        pen = QPen(QColor("#f9a825"), 2, Qt.PenStyle.DashLine)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(ir.adjusted(1, 1, -1, -1))

        # Corner handles
        c = self._CORNER
        painter.setPen(Qt.PenStyle.NoPen)
        handle_color = QColor("#f9a825")
        for _, r in self._corner_rects().items():
            painter.fillRect(r, handle_color)

        painter.end()

    # ------------------------------------------------------------------
    # Mouse events
    # ------------------------------------------------------------------

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() != Qt.MouseButton.LeftButton:
            return
        # Corner handle → resize
        for name, rect in self._corner_rects().items():
            if rect.contains(event.pos()):
                self._active = name
                self._drag_start = event.globalPosition().toPoint()
                self._geom_start = self.geometry()
                return
        # Image area (not a handle) → move
        if self._img_rect().contains(event.pos()):
            self._moving = True
            self._drag_start = event.globalPosition().toPoint()
            self._geom_start = self.geometry()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        pos = event.pos()
        # Cursor update
        for name, rect in self._corner_rects().items():
            if rect.contains(pos):
                self.setCursor(QCursor(self._CURSOR_MAP[name]))
                break
        else:
            if self._img_rect().contains(pos):
                self.setCursor(QCursor(Qt.CursorShape.SizeAllCursor))
            else:
                self.unsetCursor()

        delta = event.globalPosition().toPoint() - self._drag_start
        dx, dy = delta.x(), delta.y()
        g = QRect(self._geom_start)

        # Move
        if self._moving:
            # Clamp inside parent widget
            parent = self.parent()
            pw = parent.width()  if parent else 9999
            ph = parent.height() if parent else 9999
            nx = max(0, min(g.left() + dx, pw - g.width()))
            ny = max(0, min(g.top()  + dy, ph - g.height()))
            self.move(nx, ny)
            return

        if self._active is None:
            return

        # Resize
        lock = self._chk_lock.isChecked()
        TB = self._TB_H

        def clamped(w, h):
            w = max(self._MIN, w)
            h = max(self._MIN, h)
            if lock:
                h = max(self._MIN, round(w / self._ratio))
            return w, h

        if self._active == "br":
            nw, nh = clamped(g.width() + dx, g.height() - TB + dy)
            self.setGeometry(g.left(), g.top(), nw, nh + TB)
        elif self._active == "bl":
            nw, nh = clamped(g.width() - dx, g.height() - TB + dy)
            self.setGeometry(g.right() - nw, g.top(), nw, nh + TB)
        elif self._active == "tr":
            nw, nh = clamped(g.width() + dx, g.height() - TB - dy)
            self.setGeometry(g.left(), g.bottom() - nh - TB, nw, nh + TB)
        elif self._active == "tl":
            nw, nh = clamped(g.width() - dx, g.height() - TB - dy)
            self.setGeometry(g.right() - nw, g.bottom() - nh - TB, nw, nh + TB)

        self._sync_spinboxes()
        self._refresh_image()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self._active = None
        self._moving = False

    # ------------------------------------------------------------------
    # Resize event (keep toolbar width in sync)
    # ------------------------------------------------------------------

    def resizeEvent(self, event) -> None:
        if hasattr(self, "_tb"):
            tb_y = 0 if self._tb_above else (self.height() - self._TB_H)
            self._tb.setGeometry(0, tb_y, self.width(), self._TB_H)
        self._refresh_image()

    # ------------------------------------------------------------------
    # Spinbox ↔ geometry sync
    # ------------------------------------------------------------------

    def _sync_spinboxes(self) -> None:
        ir = self._img_rect()
        self._spin_w.blockSignals(True)
        self._spin_h.blockSignals(True)
        self._spin_w.setValue(max(self._MIN, ir.width()))
        self._spin_h.setValue(max(self._MIN, ir.height()))
        self._spin_w.blockSignals(False)
        self._spin_h.blockSignals(False)

    def _on_spin_w_changed(self, val: int) -> None:
        if self._chk_lock.isChecked():
            nh = max(self._MIN, round(val / self._ratio))
            self._spin_h.blockSignals(True)
            self._spin_h.setValue(nh)
            self._spin_h.blockSignals(False)
        g = self.geometry()
        self.resize(self._spin_w.value(), self._spin_h.value() + self._TB_H)
        self._refresh_image()

    def _on_spin_h_changed(self, val: int) -> None:
        if self._chk_lock.isChecked():
            nw = max(self._MIN, round(val * self._ratio))
            self._spin_w.blockSignals(True)
            self._spin_w.setValue(nw)
            self._spin_w.blockSignals(False)
        self.resize(self._spin_w.value(), self._spin_h.value() + self._TB_H)
        self._refresh_image()

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _on_confirm(self) -> None:
        w, h = self._spin_w.value(), self._spin_h.value()
        # Compute normalised image rect relative to the parent (PageWidget)
        parent = self.parent()
        pw = max(parent.width(),  1) if parent else 1
        ph = max(parent.height(), 1) if parent else 1
        ir = self._img_rect()
        img_x = self.pos().x() + ir.x()
        img_y = self.pos().y() + ir.y()
        norm_x = img_x       / pw
        norm_y = img_y       / ph
        norm_w = ir.width()  / pw
        norm_h = ir.height() / ph
        self.hide()
        self.deleteLater()
        self.confirmed.emit(w, h, norm_x, norm_y, norm_w, norm_h)

    def _on_cancel(self) -> None:
        self.hide()
        self.deleteLater()
        self.cancelled.emit()


# ---------------------------------------------------------------------------
# Text edit popup  (formatting toolbar + editor)
# ---------------------------------------------------------------------------
# Resize grip — thin widget overlaid on the right edge of TextEditPopup.
# Child widgets (toolbar, editor) would consume mouse events on the popup itself,
# so we use a dedicated overlay widget that sits on top of everything.
# ---------------------------------------------------------------------------

class _PopupResizeGrip(QWidget):
    """10-px blue strip pinned to the right edge of its TextEditPopup parent."""

    _W = 10  # grip width in pixels

    def __init__(self, popup: "TextEditPopup") -> None:
        super().__init__(popup)  # parent=popup → stays inside popup (correct for overlay)
        self._popup = popup
        self._drag_start_x: int = 0
        self._drag_start_w: int = 0
        self.setCursor(Qt.CursorShape.SizeHorCursor)
        self.setToolTip("Glisser pour redimensionner")
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.raise_()

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(30, 100, 220, 120))
        # Draw 3 short horizontal lines as a visual grip hint
        cx = self.width() // 2
        painter.setPen(QPen(QColor(255, 255, 255, 180), 1))
        for dy in (-4, 0, 4):
            y = self.height() // 2 + dy
            painter.drawLine(cx - 2, y, cx + 2, y)
        painter.end()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start_x = event.globalPosition().toPoint().x()
            self._drag_start_w = self._popup.width()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if event.buttons() & Qt.MouseButton.LeftButton:
            dx = event.globalPosition().toPoint().x() - self._drag_start_x
            new_w = max(400, self._drag_start_w + dx)
            screen = QApplication.screenAt(self._popup.pos())
            if screen:
                new_w = min(new_w, screen.availableGeometry().right() - self._popup.x() - 4)
            self._popup.resize(new_w, self._popup.height())
            self._popup.was_resized = True
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        event.accept()


class TextEditPopup(QWidget):
    """
    Floating popup with a formatting toolbar + QTextEdit.
    • Confirms only when user explicitly presses Enter or clicks ✓
    • Cancels (no save) on Escape, ✗, or click outside
    • confirmed(text, formatting_dict) emitted only when text changed
    """
    confirmed = Signal(str, object)   # (new_text, formatting dict)
    cancelled = Signal()
    request_eyedrop = Signal()

    TOOLBAR_H = 100   # two rows: ~52 + 48

    def __init__(self, parent: QWidget) -> None:
        # Qt.Tool : fenêtre flottante liée à la fenêtre parente (pas dans la barre des tâches)
        # FramelessWindowHint : pas de barre de titre système (on a notre propre style)
        super().__init__(
            parent,
            Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint,
        )
        self._original_text = ""
        self._drag_pos: Optional[QPoint] = None   # for dragging the popup (global coords)
        self.was_resized: bool = False             # set True when user drags the resize grip
        self._build_ui()
        self.hide()
        self.setStyleSheet(
            "TextEditPopup { background:#2b2b2b; border:2px solid #f9a825; border-radius:4px; }"
        )
        # Resize grip — created AFTER _build_ui so it sits on top
        self._grip = _PopupResizeGrip(self)
        self._grip.show()

    def resizeEvent(self, event) -> None:
        """Keep the resize grip pinned to the right edge."""
        super().resizeEvent(event)
        if hasattr(self, "_grip"):
            g = _PopupResizeGrip._W
            self._grip.setGeometry(self.width() - g, 0, g, self.height())

    # ------------------------------------------------------------------
    # Drag to reposition (toolbar area only)
    # ------------------------------------------------------------------

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton and event.pos().y() < self.TOOLBAR_H:
            self._drag_pos = event.globalPosition().toPoint()
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._drag_pos is not None:
            delta = event.globalPosition().toPoint() - self._drag_pos
            self._drag_pos = event.globalPosition().toPoint()
            new_pos = self.pos() + delta   # self.pos() est en coords écran (top-level)
            # Contraindre aux bords de l'écran courant
            screen = QApplication.screenAt(self.pos())
            if screen:
                sg = screen.availableGeometry()
                new_pos.setX(max(sg.left(), min(new_pos.x(), sg.right() - self.width())))
                new_pos.setY(max(sg.top(), min(new_pos.y(), sg.bottom() - self.height())))
            self.move(new_pos)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self._drag_pos = None
        super().mouseReleaseEvent(event)

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)

        # Shared styles
        # Use object name so background only targets the toolbar itself, NOT child buttons
        # (avoids Qt cascade bug where QWidget{background} overrides QPushButton:checked)
        SPIN_QSS = (
            "QSpinBox, QDoubleSpinBox {"
            "  background:#fff; color:#111; border:1px solid #b0b0b0; border-radius:4px;"
            "  padding:1px 6px; font-size:12px;"
            "  selection-background-color:#f9a825; }"
        )
        BTN_QSS = (
            "QPushButton { background:#e0e0e0; color:#111; border:1px solid #aaa;"
            "  border-radius:4px; }"
            "QPushButton:checked { background:#f9a825; color:#000; border-color:#c77800; }"
            "QPushButton:hover   { background:#cacaca; }"
        )
        LBL_QSS = "QLabel { color:#333; font-size:11px; font-weight:bold; background:transparent; }"

        def _sep() -> QFrame:
            """Thin vertical separator line."""
            line = QFrame()
            line.setFrameShape(QFrame.Shape.VLine)
            line.setFrameShadow(QFrame.Shadow.Sunken)
            line.setStyleSheet("QFrame { color:#c0c0c0; background:#c0c0c0; }")
            line.setFixedWidth(2)
            return line

        # ── Rangée 1 : police / format / couleur texte ──────────────────
        row1 = QWidget()
        row1.setObjectName("fmt_toolbar")
        row1.setFixedHeight(52)
        row1.setStyleSheet("#fmt_toolbar { background:#f0f0f0; }" + SPIN_QSS)
        r1 = QHBoxLayout(row1)
        r1.setContentsMargins(10, 6, 10, 6)
        r1.setSpacing(8)

        self._font_combo = QFontComboBox()
        self._font_combo.setFixedWidth(160)
        self._font_combo.setFixedHeight(34)
        self._font_combo.setToolTip("Police")
        r1.addWidget(self._font_combo)

        lbl_taille = QLabel("Taille :")
        lbl_taille.setStyleSheet(LBL_QSS)
        r1.addWidget(lbl_taille)

        self._size_spin = QSpinBox()
        self._size_spin.setRange(6, 144)
        self._size_spin.setValue(12)
        self._size_spin.setFixedWidth(58)
        self._size_spin.setFixedHeight(34)
        self._size_spin.setSuffix(" pt")
        self._size_spin.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self._size_spin.setToolTip("Taille (pt) — molette ou saisie directe")
        r1.addWidget(self._size_spin)

        r1.addWidget(_sep())

        BTN_SZ = (36, 34)
        self._btn_b = QPushButton("G")
        self._btn_b.setCheckable(True); self._btn_b.setFixedSize(*BTN_SZ)
        f = QFont(); f.setBold(True); f.setPointSize(13)
        self._btn_b.setFont(f); self._btn_b.setToolTip("Gras (Ctrl+B)")
        self._btn_b.setStyleSheet(BTN_QSS); r1.addWidget(self._btn_b)

        self._btn_i = QPushButton("I")
        self._btn_i.setCheckable(True); self._btn_i.setFixedSize(*BTN_SZ)
        fi = QFont(); fi.setItalic(True); fi.setPointSize(13)
        self._btn_i.setFont(fi); self._btn_i.setToolTip("Italique (Ctrl+I)")
        self._btn_i.setStyleSheet(BTN_QSS); r1.addWidget(self._btn_i)

        r1.addWidget(_sep())

        lbl_sp = QLabel("Espacement")
        lbl_sp.setStyleSheet(LBL_QSS); r1.addWidget(lbl_sp)

        self._spacing_spin = QDoubleSpinBox()
        self._spacing_spin.setRange(0.0, 20.0); self._spacing_spin.setSingleStep(0.5)
        self._spacing_spin.setValue(0.0); self._spacing_spin.setDecimals(1)
        self._spacing_spin.setFixedWidth(62); self._spacing_spin.setFixedHeight(34)
        self._spacing_spin.setSuffix(" px")
        self._spacing_spin.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self._spacing_spin.setToolTip("Espacement entre lettres")
        r1.addWidget(self._spacing_spin)

        r1.addWidget(_sep())

        lbl_col = QLabel("Couleur texte")
        lbl_col.setStyleSheet(LBL_QSS); r1.addWidget(lbl_col)

        self._color_btn = _ColorBtn("#000000")
        self._color_btn.setFixedSize(34, 34)
        self._color_btn.setToolTip("Couleur du texte")
        r1.addWidget(self._color_btn)

        r1.addStretch()
        layout.addWidget(row1)

        # ── Rangée 2 : couleur de fond + OK/Annuler ──────────────────────
        row2 = QWidget()
        row2.setObjectName("fmt_toolbar2")
        row2.setFixedHeight(48)
        row2.setStyleSheet("#fmt_toolbar2 { background:#e8e8e8; }" + SPIN_QSS)
        r2 = QHBoxLayout(row2)
        r2.setContentsMargins(10, 4, 10, 4)
        r2.setSpacing(8)

        lbl_bg = QLabel("Fond :")
        lbl_bg.setStyleSheet(LBL_QSS); r2.addWidget(lbl_bg)

        self._bg_color_btn = _ColorBtn("")
        self._bg_color_btn.setFixedSize(34, 34)
        self._bg_color_btn.setToolTip("Couleur de fond du texte")
        r2.addWidget(self._bg_color_btn)

        self._btn_no_bg = QPushButton("∅ Transparent")
        self._btn_no_bg.setFixedHeight(34)
        self._btn_no_bg.setToolTip("Fond transparent")
        self._btn_no_bg.setStyleSheet(BTN_QSS)
        self._btn_no_bg.clicked.connect(lambda: self._bg_color_btn.set_color("") or self._apply_fmt())
        r2.addWidget(self._btn_no_bg)

        self._btn_eyedrop = QPushButton("⊕ Pipette")
        self._btn_eyedrop.setFixedHeight(34)
        self._btn_eyedrop.setToolTip("Pipette : cliquer sur la page pour prélever une couleur de fond")
        self._btn_eyedrop.setStyleSheet(BTN_QSS)
        self._btn_eyedrop.clicked.connect(self._on_eyedrop_clicked)
        r2.addWidget(self._btn_eyedrop)

        r2.addStretch()

        btn_ok = QPushButton("✓  OK")
        btn_ok.setFixedSize(80, 34)
        btn_ok.setToolTip("Confirmer (Entrée)")
        btn_ok.setStyleSheet(
            "QPushButton { color:#fff; font-size:13px; font-weight:bold;"
            "  background:#2e7d32; border:1px solid #1b5e20; border-radius:4px; }"
            "QPushButton:hover { background:#388e3c; }"
        )
        btn_ok.clicked.connect(self._confirm)
        r2.addWidget(btn_ok)

        btn_cancel = QPushButton("✗  Annuler")
        btn_cancel.setFixedSize(90, 34)
        btn_cancel.setToolTip("Annuler (Échap)")
        btn_cancel.setStyleSheet(
            "QPushButton { color:#fff; font-size:13px; font-weight:bold;"
            "  background:#c62828; border:1px solid #7f0000; border-radius:4px; }"
            "QPushButton:hover { background:#d32f2f; }"
        )
        btn_cancel.clicked.connect(self._cancel)
        r2.addWidget(btn_cancel)

        layout.addWidget(row2)

        # --- Text editor ---
        self._editor = QTextEdit()
        self._editor.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._editor.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._editor.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self._editor.setStyleSheet(
            "QTextEdit { background:#fffde7; color:#000; border:none; padding:4px; }"
        )
        self._editor.installEventFilter(self)
        self._editor.textChanged.connect(self._auto_resize)
        layout.addWidget(self._editor)

        # Connect formatting → apply to editor
        self._font_combo.currentFontChanged.connect(self._apply_fmt)
        self._size_spin.valueChanged.connect(self._apply_fmt)
        self._btn_b.toggled.connect(self._apply_fmt)
        self._btn_i.toggled.connect(self._apply_fmt)
        self._spacing_spin.valueChanged.connect(self._apply_fmt)
        self._color_btn.color_changed.connect(self._apply_fmt)
        self._bg_color_btn.color_changed.connect(self._apply_fmt)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def show_at(
        self,
        pixel_rect: QRect,
        text: str,
        font_family: str = "Arial",
        font_size: float = 12.0,
        bold: bool = False,
        italic: bool = False,
        color: str = "#000000",
        pixel_font_h: int = 0,
        underline: bool = False,
        letter_spacing: float = 0.0,
        bg_color: str = "",
    ) -> None:
        self._original_text = text
        self._pixel_font_h = pixel_font_h if pixel_font_h > 0 else max(8, pixel_rect.height())
        self._base_pt = max(1, int(font_size))  # reference pt size for scaling
        self.was_resized = False  # reset on each new show

        for w in (self._font_combo, self._size_spin, self._btn_b,
                  self._btn_i, self._spacing_spin):
            w.blockSignals(True)

        self._font_combo.setCurrentFont(QFont(font_family))
        self._size_spin.setValue(max(6, int(font_size)))
        self._btn_b.setChecked(bold)
        self._btn_i.setChecked(italic)
        self._spacing_spin.setValue(letter_spacing)
        self._color_btn.set_color(color)
        self._bg_color_btn.set_color(bg_color)

        for w in (self._font_combo, self._size_spin, self._btn_b,
                  self._btn_i, self._spacing_spin):
            w.blockSignals(False)

        self._apply_fmt()
        self._editor.setPlainText(text)

        # Popup geometry: toolbar above, editor over the word rect
        toolbar_h = self.TOOLBAR_H + 4
        popup_w = max(pixel_rect.width(), 660)   # wide enough for row 1 (font/format/color)
        editor_h = max(40, self._pixel_font_h + 12)   # at least 40px for the text area
        popup_h = editor_h + toolbar_h + 6

        # Convertir pixel_rect (coords PageWidget) en coords écran globales
        origin = self.parent().mapToGlobal(pixel_rect.topLeft()) if self.parent() else pixel_rect.topLeft()
        gx, gy = origin.x(), origin.y()

        # Positionner : toolbar au-dessus du texte, contraindre à l'écran disponible
        screen = QApplication.screenAt(origin)
        if screen:
            sg = screen.availableGeometry()
            x = max(sg.left(), min(gx, sg.right() - popup_w))
            y = max(sg.top(), gy - toolbar_h)
            if y + popup_h > sg.bottom():   # si ça dépasse en bas, afficher au-dessus
                y = max(sg.top(), gy - popup_h)
        else:
            x, y = gx, max(0, gy - toolbar_h)

        self.setGeometry(x, y, popup_w, popup_h)
        self.show()
        self.raise_()

        cursor = self._editor.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self._editor.setTextCursor(cursor)
        self._editor.setFocus()

    # ------------------------------------------------------------------
    # Formatting
    # ------------------------------------------------------------------

    def _apply_fmt(self, *_) -> None:
        if not hasattr(self, "_pixel_font_h"):
            return  # not yet initialised via show_at()

        # Compute display point size from the pixel height of the original word
        # and the user's chosen size relative to the original.
        base_px = getattr(self, "_pixel_font_h", 16)
        base_pt = getattr(self, "_base_pt", self._size_spin.value()) or 12
        spin_pt = self._size_spin.value() or 12
        scaled_px = max(6, int(base_px * spin_pt / base_pt))
        pt_size = max(1.0, scaled_px * 72.0 / 96.0)  # pixels → points at 96 DPI

        # Build char format using individual setters — never call font.setPixelSize()
        # because that sets font.pointSize() to -1 and propagates the Qt warning
        # "QFont::setPointSize: Point size <= 0 (-1)" throughout the pipeline.
        spacing = self._spacing_spin.value()
        fmt = QTextCharFormat()
        fmt.setFontFamilies([self._font_combo.currentFont().family()])
        fmt.setFontWeight(QFont.Weight.Bold if self._btn_b.isChecked() else QFont.Weight.Normal)
        fmt.setFontItalic(self._btn_i.isChecked())
        fmt.setFontUnderline(False)
        fmt.setFontPointSize(pt_size)
        if spacing > 0:
            fmt.setFontLetterSpacing(spacing)
        fmt.setForeground(QColor(self._color_btn.color))
        saved_cursor = self._editor.textCursor()
        full_cursor = self._editor.textCursor()
        full_cursor.select(full_cursor.SelectionType.Document)
        full_cursor.mergeCharFormat(fmt)
        self._editor.setTextCursor(saved_cursor)

        _bg = self._bg_color_btn.color if self._bg_color_btn.color else "#fffde7"
        self._editor.setStyleSheet(
            f"QTextEdit {{ background:{_bg}; color:{self._color_btn.color};"
            " border:none; padding:4px; }"
        )

    def _get_fmt(self) -> dict:
        base_pt = getattr(self, "_base_pt", self._size_spin.value()) or 12
        spin_pt = self._size_spin.value() or 12
        # Store a ratio so the overlay scales correctly at any zoom level
        size_ratio = spin_pt / base_pt if base_pt else 1.0
        return {
            "font_family": self._font_combo.currentFont().family(),
            "font_size": float(spin_pt),
            "font_size_ratio": size_ratio,   # multiplier applied on top of rect.height()
            "bold": self._btn_b.isChecked(),
            "italic": self._btn_i.isChecked(),
            "underline": False,
            "letter_spacing": self._spacing_spin.value(),
            "color": self._color_btn.color,
            "bg_color": self._bg_color_btn.color,
        }

    # ------------------------------------------------------------------
    # Auto-resize popup width as text grows
    # ------------------------------------------------------------------

    def _auto_resize(self) -> None:
        from PySide6.QtGui import QFontMetricsF
        fm = QFontMetricsF(self._editor.font())
        text = self._editor.toPlainText()
        text_w = fm.horizontalAdvance(text) + 20   # padding
        min_w = max(300, int(text_w))
        if self.width() < min_w:
            geo = self.geometry()
            geo.setWidth(min_w)
            # Prevent going outside the parent widget's right edge
            parent = self.parent()
            if parent:
                max_right = parent.width() - 4
                if geo.right() > max_right:
                    geo.moveRight(max_right)
            self.setGeometry(geo)

    # ------------------------------------------------------------------
    # Confirm / cancel
    # ------------------------------------------------------------------

    def _confirm(self) -> None:
        new_text = self._editor.toPlainText()
        self.hide()
        # Always emit confirmed — consumers decide whether text or formatting actually changed.
        self.confirmed.emit(new_text, self._get_fmt())

    def _cancel(self) -> None:
        self.hide()
        self.cancelled.emit()

    # ------------------------------------------------------------------
    # Event filter on editor (keyboard shortcuts)
    # ------------------------------------------------------------------

    def eventFilter(self, obj, event: QEvent) -> bool:
        if obj is self._editor and event.type() == QEvent.Type.KeyPress:
            key = event.key()
            mods = event.modifiers()
            if key == Qt.Key.Key_Escape:
                self._cancel()
                return True
            if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                if not (mods & Qt.KeyboardModifier.ShiftModifier):
                    self._confirm()
                    return True
        return super().eventFilter(obj, event)

    def _on_eyedrop_clicked(self) -> None:
        self.request_eyedrop.emit()

    def apply_eyedrop_color(self, color: str) -> None:
        """Called back when the eyedropper samples a color from the page."""
        self._bg_color_btn.set_color(color)
        self.show()
        self._apply_fmt()


# ---------------------------------------------------------------------------
# Page widget
# ---------------------------------------------------------------------------

class PageWidget(QWidget):
    """Single page display widget."""

    annotation_drawn = Signal(str, QRectF)           # (type, normalized rect)
    form_field_drawn = Signal(QRectF)                # normalized rect — form design mode
    annotation_erase_requested = Signal(QRectF)        # normalized selection rect
    annotation_moved = Signal(str, float, float)       # (id, new_norm_x, new_norm_y)
    form_element_moved = Signal(str, str, float, float, float, float)  # (kind, name, nx, ny, nw, nh)
    comment_edit_requested = Signal(str)               # annotation id to edit
    color_sampled = Signal(str)                        # eyedropper sampled color '#rrggbb'
    comment_moved = Signal(str, float, float)          # (id, new_norm_x, new_norm_y)
    text_edit_requested = Signal(float, float)       # normalized (x, y) click
    text_selected = Signal(QRectF)                   # normalized rect of text selection
    image_click_requested = Signal(float, float)     # normalized (x, y) click on image tool
    image_draw_requested = Signal(QRectF)            # rubber-band draw in image tool (new image)
    image_context_requested = Signal(float, float)   # right-click anywhere → check for image
    image_overlay_confirmed = Signal(int, int, float, float, float, float)       # (w, h) from overlay
    image_overlay_cancelled = Signal()
    context_menu_requested = Signal(dict, int, int)  # (annotation, global_x, global_y)
    annotation_selected = Signal(dict)              # left-click on annotation in select mode
    block_pick_requested = Signal(float, float)      # move_block tool: find block at (norm_x, norm_y)
    block_move_requested = Signal(float, float, float, float, float)  # (orig_x, orig_y, new_x, new_y, new_w)
    ocr_overlay_changed = Signal(list)               # OCR items list after user resize

    _MIN_OVERLAY = 40

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._image: Optional[QImage] = None
        self._tool: str = "select"
        self._drawing = False
        self._start_pos = QPoint()
        self._rubber_band: Optional[QRubberBand] = None
        self._annotations: list[dict] = []
        self._sel_rect: Optional[QRectF] = None      # current text selection rect
        self._form_overlays: list[dict] = []          # form field overlays for designer
        self._ocr_overlay: list[dict] = []           # OCR preview items {text,nx,ny,nw,nh,color}
        self._ocr_opacity: float = 1.0
        self._ocr_bg_white: bool = False
        self._ocr_resize_idx: int = -1              # index of OCR item being resized (-1 = none)
        self._ocr_resize_start_x: float = 0.0
        self._ocr_resize_start_nw: float = 0.0
        self._OCR_HANDLE_PX: int = 8                # pixel width of resize hit zone
        self._image_overlay: Optional[_ImageOverlay] = None
        self._dragging_ann: Optional[dict] = None        # annotation being moved in select mode
        self._drag_ann_offset: tuple = (0.0, 0.0)        # click offset within annotation
        self._dragging_form: Optional[dict] = None       # form element (field/label) being moved
        self._drag_form_offset: tuple = (0.0, 0.0)
        self._form_ocr_resize: Optional[dict] = None     # OCR label being resized by right-edge handle
        self._form_ocr_resize_start_x: float = 0.0
        self._form_ocr_resize_start_nw: float = 0.0
        self._form_ocr_resize_vert: Optional[dict] = None  # OCR label being resized by bottom-edge
        self._form_ocr_resize_start_y: float = 0.0
        self._form_ocr_resize_start_nh: float = 0.0
        self._FORM_OCR_HANDLE_PX: int = 8

        # Text edit popup
        self._popup = TextEditPopup(self)
        self._popup_norm_rect: Optional[QRectF] = None
        self._popup.confirmed.connect(self._on_popup_confirmed)
        self._popup.cancelled.connect(self._on_popup_cancelled)
        self._popup.request_eyedrop.connect(self._on_eyedrop_requested)
        self._eyedrop_pending: bool = False
        self._prev_tool: str = "select"

        # Comment drag state
        self._dragging_comment: Optional[dict] = None   # dict being dragged
        self._drag_offset_norm = (0.0, 0.0)             # offset from ann origin to click point

        # Block drag state (move_block tool)
        self._block_drag_origin: Optional[tuple] = None   # (norm_x, norm_y) of press point
        self._block_drag_ghost: Optional[QRectF] = None   # original bounding box (red dashed during drag)
        self._block_drag_current: Optional[QRectF] = None # current/selected position (persistent blue)
        self._block_drag_offset: tuple = (0.0, 0.0)       # click offset within block
        self._block_is_dragging: bool = False              # body drag in progress
        self._block_is_resizing: bool = False              # right-edge resize in progress
        self._block_resize_start_x: float = 0.0           # mouse x (pixels) at resize start
        self._block_resize_start_w: float = 0.0           # ghost width at resize start
        _RESIZE_HANDLE_PX = 10
        self._resize_handle_px: int = _RESIZE_HANDLE_PX

        # Custom comment hover label (replaces QToolTip — immune to Windows native style)
        self._comment_label = QLabel("", self)
        self._comment_label.setStyleSheet(
            "QLabel { background-color: #fffde7; color: #1a1a1a;"
            " border: 1px solid #f9a825; padding: 4px 8px;"
            " font-size: 12px; border-radius: 3px; }"
        )
        self._comment_label.setWordWrap(True)
        self._comment_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._comment_label.hide()

        self.setMouseTracking(True)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    # ------------------------------------------------------------------

    def show_image_overlay(self, pil_img, norm_rect: QRectF) -> None:
        """Show a resizable image overlay at the given normalized rect."""
        if self._image_overlay is not None:
            try:
                self._image_overlay.hide()
                self._image_overlay.deleteLater()
            except RuntimeError:
                pass  # C++ object already deleted by a previous confirm/cancel
            self._image_overlay = None
        w, h = max(self.width(), 1), max(self.height(), 1)
        screen_rect = QRect(
            int(norm_rect.x() * w),
            int(norm_rect.y() * h),
            max(self._MIN_OVERLAY, int(norm_rect.width() * w)),
            max(self._MIN_OVERLAY, int(norm_rect.height() * h)),
        )
        ov = _ImageOverlay(pil_img, screen_rect, self)
        ov.confirmed.connect(self.image_overlay_confirmed)
        ov.cancelled.connect(self.image_overlay_cancelled)
        # Clear reference when overlay deletes itself (after confirm or cancel)
        ov.confirmed.connect(lambda *_: setattr(self, "_image_overlay", None))
        ov.cancelled.connect(lambda: setattr(self, "_image_overlay", None))
        self._image_overlay = ov

    def clear_image_overlay(self) -> None:
        if self._image_overlay is not None:
            try:
                self._image_overlay.hide()
                self._image_overlay.deleteLater()
            except RuntimeError:
                pass
            self._image_overlay = None

    # ------------------------------------------------------------------

    def set_image(self, image: Optional[QImage]) -> None:
        self._image = image
        self._sel_rect = None
        if image is not None:
            self.setFixedSize(image.width(), image.height())
        else:
            self.setFixedSize(0, 0)
        if self._popup.isVisible():
            self._popup.hide()
        self._comment_label.hide()
        self.update()

    def highlight_search(self, rect: Optional[QRectF]) -> None:
        """Highlight a search match (normalized coords). Pass None to clear."""
        self._sel_rect = rect
        self.update()

    def set_form_overlays(self, overlays: list[dict]) -> None:
        """Set form field overlay descriptors {nx,ny,nw,nh,name,type} and repaint."""
        self._form_overlays = overlays
        self.update()

    def set_ocr_overlay(self, items: list, opacity: float = 1.0, bg_white: bool = False) -> None:
        """Show OCR text preview overlay on top of the page (does NOT write to PDF)."""
        self._ocr_overlay = items
        self._ocr_opacity = max(0.0, min(1.0, opacity))
        self._ocr_bg_white = bg_white
        self.update()

    def clear_ocr_overlay(self) -> None:
        """Remove the OCR preview overlay."""
        self._ocr_overlay = []
        self.update()

    def set_tool(self, tool: str) -> None:
        self._tool = tool
        cursors = {
            "select":     Qt.CursorShape.ArrowCursor,
            "highlight":  Qt.CursorShape.IBeamCursor,
            "underline":  Qt.CursorShape.IBeamCursor,
            "draw":       Qt.CursorShape.CrossCursor,
            "comment":    Qt.CursorShape.PointingHandCursor,
            "text_edit":  Qt.CursorShape.IBeamCursor,
            "image":      Qt.CursorShape.PointingHandCursor,
            "erase":      Qt.CursorShape.CrossCursor,
            "form_design":Qt.CursorShape.CrossCursor,
            "eyedrop":    Qt.CursorShape.CrossCursor,
            "move_block": Qt.CursorShape.OpenHandCursor,
        }
        # Reset block drag state when switching away from move_block
        if tool != "move_block":
            self._block_drag_origin = None
            self._block_drag_ghost = None
            self._block_drag_current = None
            self._block_is_dragging = False
            self._block_is_resizing = False
        self.setCursor(QCursor(cursors.get(tool, Qt.CursorShape.ArrowCursor)))

    def set_block_ghost(self, norm_rect: QRectF, *, start_dragging: bool = True) -> None:
        """Called by main_window after block_pick_requested or after a successful move."""
        self._block_drag_ghost = norm_rect if start_dragging else None
        origin = self._block_drag_origin or (norm_rect.x(), norm_rect.y())
        self._block_drag_offset = (origin[0] - norm_rect.x(), origin[1] - norm_rect.y())
        self._block_drag_current = QRectF(norm_rect)
        self._block_is_dragging = start_dragging
        self._block_is_resizing = False
        self.update()

    def add_annotation(self, ann: dict) -> None:
        self._annotations.append(ann)
        self.update()

    def clear_annotations(self) -> None:
        self._annotations.clear()
        self.update()

    # ------------------------------------------------------------------
    # Text editor popup — called from main_window
    # ------------------------------------------------------------------

    def show_text_editor(
        self,
        norm_rect: QRectF,
        text: str,
        font_family: str = "Arial",
        font_size: float = 12.0,
        bold: bool = False,
        italic: bool = False,
        color: str = "#000000",
        underline: bool = False,
        letter_spacing: float = 0.0,
        bg_color: str = "",
    ) -> None:
        self._popup_norm_rect = norm_rect
        w, h = self.width() or 1, self.height() or 1

        # True pixel height of the word in the current rendered image
        pixel_font_h = max(8, int(norm_rect.height() * h))

        pixel_rect = QRect(
            int(norm_rect.x() * w),
            int(norm_rect.y() * h),
            max(int(norm_rect.width() * w), 300),
            pixel_font_h,
        )
        pixel_rect.setRight(min(pixel_rect.right(), w - 4))
        # Pass pixel_font_h so the editor renders at the exact same size as the PDF
        self._popup.show_at(pixel_rect, text, font_family, font_size, bold, italic, color,
                            pixel_font_h=pixel_font_h,
                            underline=underline, letter_spacing=letter_spacing,
                            bg_color=bg_color)
        # Stocker la position initiale en coords locales PageWidget (le popup est top-level,
        # donc .pos() retourne des coords écran → on convertit avec mapFromGlobal).
        local_pos = self.mapFromGlobal(self._popup.pos())
        self._popup_initial_x = local_pos.x()
        self._popup_initial_y = local_pos.y()

    # ------------------------------------------------------------------
    # Paint
    # ------------------------------------------------------------------

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        if self._image:
            painter.drawImage(0, 0, self._image)
        for ann in self._annotations:
            self._paint_annotation(painter, ann)
        # Draw text selection highlight
        if self._sel_rect is not None:
            w, h = self.width(), self.height()
            r = QRectF(
                self._sel_rect.x() * w, self._sel_rect.y() * h,
                self._sel_rect.width() * w, self._sel_rect.height() * h,
            )
            sel_color = QColor(30, 120, 255, 70)
            painter.fillRect(r, sel_color)
            painter.setPen(QPen(QColor(30, 100, 220), 1))
            painter.drawRect(r)
        # Draw form field overlays (designer mode)
        if self._form_overlays:
            w, h = self.width(), self.height()
            for ov in self._form_overlays:
                r = QRectF(ov["nx"] * w, ov["ny"] * h, ov["nw"] * w, ov["nh"] * h)
                painter.fillRect(r, QColor(0, 160, 110, 45))
                painter.setPen(QPen(QColor(0, 130, 90), 1, Qt.PenStyle.DashLine))
                painter.drawRect(r)
                # For "texte" blocks pdfium already renders the content;
                # only show the field name label for non-texte annotations.
                if ov.get("ftype", "label") != "texte":
                    painter.setPen(QPen(QColor(0, 90, 60)))
                    painter.setFont(QFont("Arial", 8))
                    painter.drawText(
                        r.adjusted(3, 2, -2, -2),
                        Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft,
                        ov.get("name", ""),
                    )
                # Resize handles (right edge + bottom edge) for OCR injected labels
                if ov.get("is_ocr"):
                    _hw = self._FORM_OCR_HANDLE_PX
                    # Right-edge handle
                    handle_x = min(r.right() - _hw, w - _hw - 2)
                    painter.fillRect(
                        QRectF(handle_x, r.top() + 1, _hw, r.height() - 2),
                        QColor(80, 80, 200, 200),
                    )
                    # Bottom-edge handle
                    handle_y = min(r.bottom() - _hw, h - _hw - 2)
                    painter.fillRect(
                        QRectF(r.left() + 1, handle_y, r.width() - 2, _hw),
                        QColor(80, 80, 200, 200),
                    )
        # Draw block drag ghost (move_block tool)
        if self._block_drag_ghost is not None or self._block_drag_current is not None:
            w, h = self.width(), self.height()
            # Original position: red dashed outline (only while actively dragging/resizing)
            if self._block_drag_ghost is not None:
                orig = self._block_drag_ghost
                r_orig = QRectF(orig.x() * w, orig.y() * h, orig.width() * w, orig.height() * h)
                painter.setPen(QPen(QColor(220, 60, 60, 160), 1, Qt.PenStyle.DashLine))
                painter.drawRect(r_orig)
            # Current position: blue semi-transparent fill + solid outline + resize handle
            if self._block_drag_current is not None:
                cur = self._block_drag_current
                r_cur = QRectF(cur.x() * w, cur.y() * h, cur.width() * w, cur.height() * h)
                painter.fillRect(r_cur, QColor(30, 120, 255, 30))
                painter.setPen(QPen(QColor(30, 100, 220), 2))
                painter.drawRect(r_cur)
                # Resize handle: small white rect with blue border at right edge
                hpx = self._resize_handle_px
                hr = QRectF(r_cur.right() - hpx, r_cur.top(), hpx, r_cur.height())
                painter.fillRect(hr, QColor(255, 255, 255, 180))
                painter.setPen(QPen(QColor(30, 100, 220), 1))
                painter.drawRect(hr)
                # Draw ↔ arrows hint in the handle
                mid_y = int(r_cur.top() + r_cur.height() / 2)
                mx = int(r_cur.right() - hpx / 2)
                painter.setPen(QPen(QColor(30, 100, 220), 1))
                painter.drawLine(mx - 3, mid_y, mx + 3, mid_y)
                painter.drawLine(mx - 3, mid_y, mx - 1, mid_y - 2)
                painter.drawLine(mx - 3, mid_y, mx - 1, mid_y + 2)
                painter.drawLine(mx + 3, mid_y, mx + 1, mid_y - 2)
                painter.drawLine(mx + 3, mid_y, mx + 1, mid_y + 2)
        # Draw OCR preview overlay (dynamic, not written to PDF)
        if self._ocr_overlay:
            w, h = self.width(), self.height()
            alpha = int(self._ocr_opacity * 255)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            for item in self._ocr_overlay:
                px = item["nx"] * w
                py = item["ny"] * h
                bw = item["nw"] * w
                bh = item["nh"] * h
                if bw < 1 or bh < 1:
                    continue
                # Visible portion is clipped to widget width
                vis_bw = min(bw, w - px)
                if self._ocr_bg_white:
                    painter.fillRect(QRectF(px, py, vis_bw, bh),
                                     QColor(255, 255, 255, alpha))
                color = QColor(item.get("color", "#000000"))
                color.setAlpha(alpha)
                font = QFont("Helvetica")
                font.setPixelSize(max(4, int(bh * 0.72)))
                painter.setFont(font)
                painter.setPen(QPen(color))
                painter.drawText(
                    QRectF(px + 2, py, vis_bw - 2, bh),
                    Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
                    item["text"],
                )
                # Resize handle: always visible, clamped so it stays inside the widget
                _hw = 6  # handle width px
                handle_x = min(px + bw - _hw, w - _hw - 2)
                painter.fillRect(
                    QRectF(handle_x, py + 1, _hw, bh - 2),
                    QColor(80, 80, 200, 200),
                )
        painter.end()

    def _paint_annotation(self, painter: QPainter, ann: dict) -> None:
        w, h = self.width(), self.height()
        rect = QRectF(
            ann["x"] * w, ann["y"] * h,
            ann["width"] * w, ann["height"] * h,
        )
        ann_type = ann.get("type", "highlight")
        color = QColor(ann.get("color", "#FFFF00"))

        if ann_type == "highlight":
            color.setAlpha(80)
            painter.fillRect(rect, color)
        elif ann_type == "underline":
            pen = QPen(color, 2)
            painter.setPen(pen)
            y = rect.bottom()
            painter.drawLine(int(rect.left()), int(y), int(rect.right()), int(y))
        elif ann_type == "comment":
            # Draw a sticky-note icon: size scales with zoom (rect already in screen pixels)
            note_size = max(16, int(rect.width()))
            note_rect = QRectF(rect.x(), rect.y(), note_size, note_size)
            bg_color = QColor(color)
            bg_color.setAlpha(210)
            painter.fillRect(note_rect, bg_color)
            painter.setPen(QPen(color, 1))
            painter.drawRect(note_rect)
            painter.setPen(QPen(QColor("#000000")))
            painter.setFont(QFont("Arial", max(8, note_size - 10)))
            painter.drawText(note_rect, Qt.AlignmentFlag.AlignCenter, "\u270e")
        elif ann_type == "freetext":
            # Font pixel size scales with zoom: use rect.height() as base
            # (rect is already in screen pixels at current zoom), then apply
            # the user's size-ratio adjustment stored at annotation creation.
            base_px = max(6, int(rect.height()))
            size_ratio = ann.get("font_size_ratio", 1.0) or 1.0
            pixel_h = max(6, int(base_px * size_ratio))
            font = QFont(ann.get("font_family", "Arial"))
            font.setPixelSize(pixel_h)
            font.setBold(ann.get("bold", False))
            font.setItalic(ann.get("italic", False))
            font.setUnderline(ann.get("underline", False))
            spacing = ann.get("letter_spacing", 0.0) or 0.0
            if spacing > 0:
                font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, spacing)

            from PySide6.QtGui import QFontMetricsF
            fm = QFontMetricsF(font)
            text_str = ann.get("text", "")
            text_w = fm.horizontalAdvance(text_str) + 4
            draw_rect = QRectF(
                rect.x(), rect.y(),
                max(rect.width(), text_w),
                rect.height(),
            )

            # Background fill: only if an explicit bg_color is set.
            # Transparent (bg_color="") → skip fill so page content shows through.
            _ann_bg = ann.get("bg_color", "")
            if _ann_bg:
                painter.fillRect(
                    draw_rect.adjusted(-1, -2, 1, 2), QColor(_ann_bg)
                )

            painter.setFont(font)
            painter.setPen(QPen(QColor(ann.get("color", "#000000"))))
            painter.drawText(
                draw_rect,
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                text_str,
            )

    # ------------------------------------------------------------------
    # Mouse events
    # ------------------------------------------------------------------

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.RightButton:
            # Right-click: check if there is an image under the cursor (any tool)
            w, h = self.width() or 1, self.height() or 1
            self.image_context_requested.emit(
                event.pos().x() / w,
                event.pos().y() / h,
            )
            return
        if event.button() != Qt.MouseButton.LeftButton:
            return

        # Close popup on outside click
        # Le popup est top-level → geometry() est en coords écran ; event.pos() est local.
        if self._popup.isVisible():
            global_click = self.mapToGlobal(event.pos())
            if not self._popup.geometry().contains(global_click):
                self._popup._cancel()
            return

        if self._tool == "eyedrop":
            color = self._sample_color_at(event.pos())
            self._drawing = False
            self.color_sampled.emit(color)
            if self._eyedrop_pending:
                self._eyedrop_pending = False
                self._popup.apply_eyedrop_color(color)
                self.set_tool(self._prev_tool)
                self.setCursor(Qt.CursorShape.ArrowCursor)
            return

        # OCR overlay resize: check right-edge handle regardless of current tool
        if self._ocr_overlay:
            w, h = self.width() or 1, self.height() or 1
            px, py = event.pos().x(), event.pos().y()
            _hw = 6  # must match paint code
            for i, item in enumerate(self._ocr_overlay):
                raw_right = (item["nx"] + item["nw"]) * w
                # Clamped handle position matches what was painted
                handle_x = min(raw_right - _hw, w - _hw - 2)
                top_px = item["ny"] * h
                bot_px = top_px + item["nh"] * h
                if (handle_x - 4 <= px <= handle_x + _hw + 4
                        and top_px - 2 <= py <= bot_px + 2):
                    self._ocr_resize_idx = i
                    self._ocr_resize_start_x = px
                    self._ocr_resize_start_nw = item["nw"]
                    self.setCursor(Qt.CursorShape.SizeHorCursor)
                    event.accept()
                    return

        self._start_pos = event.pos()
        self._drawing = True

        if self._tool == "text_edit":
            w, h = self.width() or 1, self.height() or 1
            self.text_edit_requested.emit(
                event.pos().x() / w,
                event.pos().y() / h,
            )
            self._drawing = False
            return

        if self._tool == "move_block":
            w, h = self.width() or 1, self.height() or 1
            px, py = event.pos().x(), event.pos().y()
            nx, ny = px / w, py / h
            self._drawing = False

            # If a block is already selected, check for resize handle or body drag
            if self._block_drag_current is not None:
                cur = self._block_drag_current
                # Pixel coords of current ghost
                bx = cur.x() * w
                by = cur.y() * h
                bw = cur.width() * w
                bh = cur.height() * h
                handle_x0 = bx + bw - self._resize_handle_px

                # Click on right-edge resize handle?
                if handle_x0 <= px <= bx + bw + 2 and by - 2 <= py <= by + bh + 2:
                    self._block_is_resizing = True
                    self._block_is_dragging = False
                    self._block_resize_start_x = px
                    self._block_resize_start_w = cur.width()
                    self._block_drag_ghost = QRectF(cur)  # red outline = original pos
                    self.setCursor(Qt.CursorShape.SizeHorCursor)
                    return

                # Click on block body?
                if bx - 4 <= px <= bx + bw + 4 and by - 4 <= py <= by + bh + 4:
                    self._block_is_dragging = True
                    self._block_is_resizing = False
                    self._block_drag_origin = (nx, ny)
                    self._block_drag_offset = (nx - cur.x(), ny - cur.y())
                    self._block_drag_ghost = QRectF(cur)  # red outline = original pos
                    self.setCursor(Qt.CursorShape.ClosedHandCursor)
                    return

                # Click outside selected block → deselect and start new pick below
                self._block_drag_current = None
                self._block_drag_ghost = None
                self._block_is_dragging = False
                self._block_is_resizing = False
                self.update()

            # New pick
            self._block_drag_origin = (nx, ny)
            self._block_drag_ghost = None
            self._block_drag_current = None
            self._block_is_dragging = False
            self._block_is_resizing = False
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            self.block_pick_requested.emit(nx, ny)  # main_window will call set_block_ghost()
            return

        if self._tool == "comment":
            existing = self._comment_at(event.pos())
            if existing is not None:
                # Start dragging the existing comment
                self._drawing = False
                self._dragging_comment = existing
                w, h = self.width() or 1, self.height() or 1
                nx, ny = event.pos().x() / w, event.pos().y() / h
                self._drag_offset_norm = (nx - existing["x"], ny - existing["y"])
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
                return
            # Single click on empty area: place a new comment note
            w, h = self.width() or 1, self.height() or 1
            note_px = 24
            norm = QRectF(
                event.pos().x() / w,
                event.pos().y() / h,
                note_px / w,
                note_px / h,
            )
            self.annotation_drawn.emit(self._tool, norm)
            self._drawing = False
            return

        if self._tool == "image":
            # Start rubber-band; decide click vs drag on mouseRelease
            self._rubber_band = QRubberBand(QRubberBand.Shape.Rectangle, self)
            self._rubber_band.setGeometry(QRect(self._start_pos, QSize()))
            self._rubber_band.show()
            return

        if self._tool == "select":
            # In select mode, clicking on an annotation starts moving it
            ann = self._annotation_at(event.pos())
            if ann:
                self._drawing = False
                self._dragging_ann = ann
                w, h = self.width() or 1, self.height() or 1
                nx, ny = event.pos().x() / w, event.pos().y() / h
                self._drag_ann_offset = (nx - ann["x"], ny - ann["y"])
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
                self.annotation_selected.emit(ann)
                return
            # Check OCR label resize handles (right-edge + bottom-edge) before general form drag
            if self._form_overlays:
                w, h = self.width() or 1, self.height() or 1
                px_click, py_click = event.pos().x(), event.pos().y()
                _hw = self._FORM_OCR_HANDLE_PX
                for ov in reversed(self._form_overlays):
                    if not ov.get("is_ocr"):
                        continue
                    top_px = ov["ny"] * h
                    bot_px = top_px + ov["nh"] * h
                    left_px = ov["nx"] * w
                    raw_right = (ov["nx"] + ov["nw"]) * w
                    handle_x = min(raw_right - _hw, w - _hw - 2)
                    handle_y = min(bot_px - _hw, h - _hw - 2)
                    # Right-edge handle
                    if (handle_x - 4 <= px_click <= handle_x + _hw + 4
                            and top_px - 2 <= py_click <= bot_px + 2):
                        self._drawing = False
                        self._form_ocr_resize = ov
                        self._form_ocr_resize_start_x = px_click
                        self._form_ocr_resize_start_nw = ov["nw"]
                        self.setCursor(Qt.CursorShape.SizeHorCursor)
                        event.accept()
                        return
                    # Bottom-edge handle (exclude right-handle zone to avoid overlap in corner)
                    if (left_px - 2 <= px_click <= handle_x - 4
                            and handle_y - 4 <= py_click <= handle_y + _hw + 4):
                        self._drawing = False
                        self._form_ocr_resize_vert = ov
                        self._form_ocr_resize_start_y = py_click
                        self._form_ocr_resize_start_nh = ov["nh"]
                        self.setCursor(Qt.CursorShape.SizeVerCursor)
                        event.accept()
                        return
            # Check form elements (fields + labels)
            ov = self._form_element_at(event.pos())
            if ov:
                self._drawing = False
                self._dragging_form = ov
                self._drag_form_start = (ov["nx"], ov["ny"])   # remember start
                w, h = self.width() or 1, self.height() or 1
                nx, ny = event.pos().x() / w, event.pos().y() / h
                self._drag_form_offset = (nx - ov["nx"], ny - ov["ny"])
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
                return
            # No annotation under cursor — rubber band text selection
            self._rubber_band = QRubberBand(QRubberBand.Shape.Rectangle, self)
            self._rubber_band.setGeometry(QRect(self._start_pos, QSize()))
            self._rubber_band.show()
            return

        if self._tool in ("erase", "highlight", "underline", "form_design"):
            self._rubber_band = QRubberBand(QRubberBand.Shape.Rectangle, self)
            self._rubber_band.setGeometry(QRect(self._start_pos, QSize()))
            self._rubber_band.show()

    def _comment_at(self, pos: QPoint) -> Optional[dict]:
        """Return the comment annotation under *pos* (screen pixels), or None."""
        w, h = self.width() or 1, self.height() or 1
        nx, ny = pos.x() / w, pos.y() / h
        for ann in reversed(self._annotations):
            if ann.get("type") != "comment":
                continue
            note_norm_size = 28 / min(w, h)   # approximate icon size in norm coords
            ann_w = max(ann.get("width", 0), note_norm_size)
            ann_h = max(ann.get("height", 0), note_norm_size)
            if (ann["x"] <= nx <= ann["x"] + ann_w and
                    ann["y"] <= ny <= ann["y"] + ann_h):
                return ann
        return None

    def _annotation_at(self, pos: QPoint) -> Optional[dict]:
        """Return any annotation (any type) under *pos* (screen pixels), or None."""
        w, h = self.width() or 1, self.height() or 1
        nx, ny = pos.x() / w, pos.y() / h
        for ann in reversed(self._annotations):
            ann_w = ann.get("width", 0)
            ann_h = ann.get("height", 0)
            if ann.get("type") == "comment":
                note_norm_size = 28 / min(w, h)
                ann_w = max(ann_w, note_norm_size)
                ann_h = max(ann_h, note_norm_size)
            if (ann["x"] <= nx <= ann["x"] + ann_w and
                    ann["y"] <= ny <= ann["y"] + ann_h):
                return ann
        return None

    def _form_element_at(self, pos: QPoint) -> Optional[dict]:
        """Return a form overlay (field or label) dict under *pos*, or None."""
        if not self._form_overlays:
            return None
        w, h = self.width() or 1, self.height() or 1
        nx, ny = pos.x() / w, pos.y() / h
        for ov in reversed(self._form_overlays):
            if (ov["nx"] <= nx <= ov["nx"] + ov["nw"] and
                    ov["ny"] <= ny <= ov["ny"] + ov["nh"]):
                return ov
        return None

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        # OCR overlay resize in progress
        if self._ocr_resize_idx >= 0:
            w = self.width() or 1
            dx = event.pos().x() - self._ocr_resize_start_x
            item = self._ocr_overlay[self._ocr_resize_idx]
            new_nw = max(0.02, self._ocr_resize_start_nw + dx / w)
            new_nw = min(new_nw, 1.0 - item["nx"])
            item["nw"] = new_nw
            self.update()
            event.accept()
            return

        # Cursor: show SizeHor/SizeVer over OCR form label resize handles (select mode)
        if (self._form_ocr_resize is None and self._form_ocr_resize_vert is None
                and self._dragging_form is None
                and self._tool == "select" and self._form_overlays):
            w, h = self.width() or 1, self.height() or 1
            px_h, py_h = event.pos().x(), event.pos().y()
            _hw = self._FORM_OCR_HANDLE_PX
            _found_handle = False
            for ov in self._form_overlays:
                if not ov.get("is_ocr"):
                    continue
                top_px = ov["ny"] * h
                bot_px = top_px + ov["nh"] * h
                left_px = ov["nx"] * w
                raw_right = (ov["nx"] + ov["nw"]) * w
                handle_x = min(raw_right - _hw, w - _hw - 2)
                handle_y = min(bot_px - _hw, h - _hw - 2)
                if (handle_x - 4 <= px_h <= handle_x + _hw + 4
                        and top_px - 2 <= py_h <= bot_px + 2):
                    self.setCursor(Qt.CursorShape.SizeHorCursor)
                    _found_handle = True
                    break
                if (left_px - 2 <= px_h <= raw_right + 2
                        and handle_y - 4 <= py_h <= handle_y + _hw + 4):
                    self.setCursor(Qt.CursorShape.SizeVerCursor)
                    _found_handle = True
                    break
            if not _found_handle and self._ocr_resize_idx < 0:
                self.unsetCursor()

        # Cursor: show SizeHor when hovering near the (clamped) resize handle of any OCR item
        if self._ocr_overlay and self._ocr_resize_idx < 0:
            w, h = self.width() or 1, self.height() or 1
            px, py = event.pos().x(), event.pos().y()
            _hw = 6
            for item in self._ocr_overlay:
                raw_right = (item["nx"] + item["nw"]) * w
                handle_x = min(raw_right - _hw, w - _hw - 2)
                top_px = item["ny"] * h
                bot_px = top_px + item["nh"] * h
                if (handle_x - 4 <= px <= handle_x + _hw + 4
                        and top_px - 2 <= py <= bot_px + 2):
                    self.setCursor(Qt.CursorShape.SizeHorCursor)
                    return
            self.unsetCursor()

        # Resize OCR form label via right-edge handle
        if self._form_ocr_resize is not None:
            w = self.width() or 1
            dx = event.pos().x() - self._form_ocr_resize_start_x
            ov = self._form_ocr_resize
            ov["nw"] = max(0.02, min(self._form_ocr_resize_start_nw + dx / w, 1.0 - ov["nx"]))
            self.update()
            event.accept()
            return

        # Resize OCR form label via bottom-edge handle
        if self._form_ocr_resize_vert is not None:
            h = self.height() or 1
            dy = event.pos().y() - self._form_ocr_resize_start_y
            ov = self._form_ocr_resize_vert
            ov["nh"] = max(0.005, min(self._form_ocr_resize_start_nh + dy / h, 1.0 - ov["ny"]))
            self.update()
            event.accept()
            return

        # Drag a form element (field or label) in select mode
        if self._dragging_form is not None:
            ov = self._dragging_form
            w, h = self.width() or 1, self.height() or 1
            nx = event.pos().x() / w - self._drag_form_offset[0]
            ny = event.pos().y() / h - self._drag_form_offset[1]
            nx = max(0.0, min(nx, 1.0 - ov["nw"]))
            ny = max(0.0, min(ny, 1.0 - ov["nh"]))
            ov["nx"] = nx
            ov["ny"] = ny
            self.update()
            return

        # Drag any annotation in select mode
        if self._dragging_ann is not None:
            w, h = self.width() or 1, self.height() or 1
            nx = event.pos().x() / w - self._drag_ann_offset[0]
            ny = event.pos().y() / h - self._drag_ann_offset[1]
            nx = max(0.0, min(nx, 1.0 - self._dragging_ann.get("width", 0)))
            ny = max(0.0, min(ny, 1.0 - self._dragging_ann.get("height", 0)))
            self._dragging_ann["x"] = nx
            self._dragging_ann["y"] = ny
            self.update()
            return

        # Drag an existing comment in comment tool mode
        if self._dragging_comment is not None:
            w, h = self.width() or 1, self.height() or 1
            nx = event.pos().x() / w - self._drag_offset_norm[0]
            ny = event.pos().y() / h - self._drag_offset_norm[1]
            # Clamp to widget bounds
            nx = max(0.0, min(nx, 1.0 - self._dragging_comment.get("width", 0)))
            ny = max(0.0, min(ny, 1.0 - self._dragging_comment.get("height", 0)))
            self._dragging_comment["x"] = nx
            self._dragging_comment["y"] = ny
            self._comment_label.hide()
            self.update()
            return

        # Resize a block (right-edge drag)
        if self._block_is_resizing and self._block_drag_current is not None:
            w = self.width() or 1
            dx = (event.pos().x() - self._block_resize_start_x) / w
            new_w = max(0.04, self._block_resize_start_w + dx)
            new_w = min(new_w, 1.0 - self._block_drag_current.x())
            self._block_drag_current = QRectF(
                self._block_drag_current.x(),
                self._block_drag_current.y(),
                new_w,
                self._block_drag_current.height(),
            )
            self.update()
            return

        # Drag a text block body in move_block mode
        if self._block_is_dragging and self._block_drag_ghost is not None:
            w, h = self.width() or 1, self.height() or 1
            nx = event.pos().x() / w - self._block_drag_offset[0]
            ny = event.pos().y() / h - self._block_drag_offset[1]
            nx = max(0.0, min(nx, 1.0 - self._block_drag_ghost.width()))
            ny = max(0.0, min(ny, 1.0 - self._block_drag_ghost.height()))
            self._block_drag_current = QRectF(
                nx, ny,
                self._block_drag_ghost.width(),
                self._block_drag_ghost.height(),
            )
            self.update()
            return

        # Update cursor when hovering over a selected (but not dragged) block
        if (self._tool == "move_block" and self._block_drag_current is not None
                and not self._block_is_dragging and not self._block_is_resizing):
            cur = self._block_drag_current
            w, h = self.width() or 1, self.height() or 1
            px, py = event.pos().x(), event.pos().y()
            bx = cur.x() * w
            by = cur.y() * h
            bw = cur.width() * w
            bh = cur.height() * h
            if bx + bw - self._resize_handle_px <= px <= bx + bw + 2 and by - 2 <= py <= by + bh + 2:
                self.setCursor(Qt.CursorShape.SizeHorCursor)
            elif bx - 4 <= px <= bx + bw + 4 and by - 4 <= py <= by + bh + 4:
                self.setCursor(Qt.CursorShape.OpenHandCursor)
            else:
                self.setCursor(Qt.CursorShape.OpenHandCursor)
            return

        if self._drawing and self._rubber_band:
            self._rubber_band.setGeometry(
                QRect(self._start_pos, event.pos()).normalized()
            )
        # Show custom hover label when over a comment annotation
        ann = self._comment_at(event.pos())
        if ann and ann.get("text"):
            self._comment_label.setText(ann["text"])
            self._comment_label.adjustSize()
            # Position label to the bottom-right of the cursor, clamped to widget bounds
            px = min(event.pos().x() + 14, self.width()  - self._comment_label.width()  - 4)
            py = min(event.pos().y() + 14, self.height() - self._comment_label.height() - 4)
            self._comment_label.move(max(0, px), max(0, py))
            self._comment_label.show()
            self._comment_label.raise_()
        else:
            self._comment_label.hide()
        # Hover cursor: open hand over movable annotations and form elements in select mode
        if self._tool == "select" and not self._drawing:
            if (self._annotation_at(event.pos()) is not None or
                    self._form_element_at(event.pos()) is not None):
                self.setCursor(Qt.CursorShape.OpenHandCursor)
            else:
                self.unsetCursor()
        # Update cursor when hovering over a comment
        elif self._tool == "comment":
            if self._comment_at(event.pos()) is not None:
                self.setCursor(Qt.CursorShape.OpenHandCursor)
            else:
                self.unsetCursor()

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        """Double-click: edit comment if on one, otherwise trigger text edit at position."""
        if event.button() != Qt.MouseButton.LeftButton:
            return
        ann = self._comment_at(event.pos())
        if ann and ann.get("id"):
            self.comment_edit_requested.emit(ann["id"])
            return
        # Double-click on page → text edit mode at that position
        w, h = self.width() or 1, self.height() or 1
        self.text_edit_requested.emit(
            event.pos().x() / w,
            event.pos().y() / h,
        )

    def annotation_at_norm(self, norm_x: float, norm_y: float) -> Optional[dict]:
        """Public: return the annotation under normalised (norm_x, norm_y), or None."""
        w, h = self.width() or 1, self.height() or 1
        return self._annotation_at(QPoint(int(norm_x * w), int(norm_y * h)))

    def contextMenuEvent(self, event) -> None:
        """Right-click: fallback for annotation context menu (keyboard Context key etc.)."""
        ann = self._annotation_at(event.pos())
        if ann:
            self.context_menu_requested.emit(ann, event.globalPos().x(), event.globalPos().y())
        else:
            event.ignore()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        # Finalize OCR overlay resize
        if self._ocr_resize_idx >= 0:
            self._ocr_resize_idx = -1
            self.unsetCursor()
            self.ocr_overlay_changed.emit(list(self._ocr_overlay))
            event.accept()
            return

        # Finalize OCR label right-edge resize
        if self._form_ocr_resize is not None:
            ov = self._form_ocr_resize
            self._form_ocr_resize = None
            self.unsetCursor()
            self.form_element_moved.emit(
                ov.get("kind", "label"), ov["name"],
                ov["nx"], ov["ny"], ov["nw"], ov["nh"],
            )
            return

        # Finalize OCR label bottom-edge resize
        if self._form_ocr_resize_vert is not None:
            ov = self._form_ocr_resize_vert
            self._form_ocr_resize_vert = None
            self.unsetCursor()
            self.form_element_moved.emit(
                ov.get("kind", "label"), ov["name"],
                ov["nx"], ov["ny"], ov["nw"], ov["nh"],
            )
            return

        # Finalize form element move — only persist if position actually changed
        if self._dragging_form is not None:
            ov = self._dragging_form
            start = getattr(self, "_drag_form_start", (ov["nx"], ov["ny"]))
            self._dragging_form = None
            self.unsetCursor()
            if abs(ov["nx"] - start[0]) > 0.004 or abs(ov["ny"] - start[1]) > 0.004:
                self.form_element_moved.emit(
                    ov.get("kind", "field"), ov["name"],
                    ov["nx"], ov["ny"], ov["nw"], ov["nh"],
                )
            return

        # Finalize annotation move (select mode)
        if self._dragging_ann is not None:
            ann = self._dragging_ann
            self._dragging_ann = None
            self.unsetCursor()
            if ann.get("id"):
                self.annotation_moved.emit(ann["id"], ann["x"], ann["y"])
            return

        # Finalize a comment drag
        if self._dragging_comment is not None:
            ann = self._dragging_comment
            self._dragging_comment = None
            self.unsetCursor()
            if ann.get("id"):
                self.comment_moved.emit(ann["id"], ann["x"], ann["y"])
            return

        # Finalize block drag or resize in move_block mode
        if self._tool == "move_block" and (self._block_is_dragging or self._block_is_resizing):
            orig = self._block_drag_origin or (0.0, 0.0)
            cur = self._block_drag_current
            # Keep ghost at final position (persistent selection)
            self._block_drag_ghost = None
            self._block_drag_origin = None
            self._block_is_dragging = False
            self._block_is_resizing = False
            self.setCursor(Qt.CursorShape.OpenHandCursor)
            self.update()
            if cur is not None:
                self.block_move_requested.emit(orig[0], orig[1], cur.x(), cur.y(), cur.width())
            return

        if not self._drawing:
            return
        self._drawing = False
        if self._rubber_band:
            self._rubber_band.hide()
            rect = QRect(self._start_pos, event.pos()).normalized()
            w, h = self.width() or 1, self.height() or 1

            # For erase: emit even for small rects / clicks (expand click to 1×1 minimum)
            if self._tool == "erase":
                er = rect if (rect.width() > 1 and rect.height() > 1) else \
                    QRect(self._start_pos.x() - 2, self._start_pos.y() - 2, 4, 4)
                norm_e = QRectF(
                    er.x() / w, er.y() / h,
                    er.width() / w, er.height() / h,
                )
                self.annotation_erase_requested.emit(norm_e)
                self._rubber_band = None
                return

            if rect.width() > 4 and rect.height() > 4:
                norm = QRectF(
                    rect.x() / w, rect.y() / h,
                    rect.width() / w, rect.height() / h,
                )
                if self._tool == "select":
                    self._sel_rect = norm
                    self.update()
                    self.text_selected.emit(norm)
                elif self._tool == "image":
                    self.image_draw_requested.emit(norm)
                elif self._tool == "form_design":
                    self.form_field_drawn.emit(norm)
                else:
                    self.annotation_drawn.emit(self._tool, norm)
            elif self._tool == "select":
                # Single click → clear selection
                self._sel_rect = None
                self.update()
            elif self._tool == "image":
                # Small drag / click → look for existing image
                self.image_click_requested.emit(
                    self._start_pos.x() / w,
                    self._start_pos.y() / h,
                )
            self._rubber_band = None

    # ------------------------------------------------------------------
    # Popup callbacks
    # ------------------------------------------------------------------

    def _on_popup_confirmed(self, text: str, fmt: dict) -> None:
        if self._popup_norm_rect is None:
            return
        # If the popup was dragged to a new position, update norm_rect accordingly.
        # Compare against the INITIAL popup position (after auto-clamping in show_at),
        # not against the original word position — to avoid treating auto-clamp as user-move.
        w, h = self.width() or 1, self.height() or 1
        # Le popup est top-level → convertir pos() écran → coords locales PageWidget
        popup_pos = self.mapFromGlobal(self._popup.pos())
        toolbar_h = self._popup.TOOLBAR_H + 4  # two rows + layout margin
        new_x = self._popup_norm_rect.x()
        new_y = self._popup_norm_rect.y()
        # Initial popup position stored by show_text_editor after show_at
        init_x = getattr(self, '_popup_initial_x', int(new_x * w))
        init_y = getattr(self, '_popup_initial_y', int(new_y * h) - toolbar_h)
        new_screen_y = popup_pos.y() + toolbar_h
        init_screen_y = init_y + toolbar_h
        user_moved_x = abs(popup_pos.x() - init_x) > 4
        user_moved_y = abs(new_screen_y - init_screen_y) > 4
        if user_moved_x or user_moved_y:
            new_x = popup_pos.x() / w
            new_y = new_screen_y / h
        # Width: if the user manually dragged the resize handle, use the popup width.
        # Otherwise auto-fit to the text content (+ one char of padding).
        if self._popup.was_resized:
            new_w = min(self._popup.width() / w, 1.0 - new_x)
        else:
            from PySide6.QtGui import QFontMetricsF as _QFM, QFont as _QFont
            _f = _QFont(self._popup._font_combo.currentFont().family())
            _f.setPointSizeF(max(1.0, self._popup._size_spin.value()))
            _fm = _QFM(_f)
            _text_px = _fm.horizontalAdvance(text) + _fm.averageCharWidth() * 2 + 8
            auto_nw = min(max(_text_px / w, 0.05), 1.0 - new_x)
            new_w = max(auto_nw, 0.05)
        # Height: fit exactly one line at the chosen font size (+ small margin).
        from PySide6.QtGui import QFontMetricsF as _QFM, QFont as _QFont
        _fh = _QFont(self._popup._font_combo.currentFont().family())
        _fh.setPointSizeF(max(1.0, self._popup._size_spin.value()))
        _fmh = _QFM(_fh)
        new_h = min(max((_fmh.height() + 6) / h, 0.008), 1.0 - new_y)
        self._popup_norm_rect = QRectF(new_x, new_y, new_w, new_h)
        # Bubble up to PDFViewer
        parent = self.parent()
        while parent and not isinstance(parent, PDFViewer):
            parent = parent.parent()
        if isinstance(parent, PDFViewer):
            parent.text_edit_confirmed.emit(self._popup_norm_rect, text, fmt)
        self._popup_norm_rect = None

    def _on_popup_cancelled(self) -> None:
        self._popup_norm_rect = None

    def _on_eyedrop_requested(self) -> None:
        """Switch to eyedrop mode to sample a background color for the inline editor."""
        self._prev_tool = self._tool
        self._eyedrop_pending = True
        self.set_tool("eyedrop")
        self._popup.hide()
        self.setCursor(Qt.CursorShape.CrossCursor)

    def _sample_color_at(self, pos: "QPoint") -> str:
        """Return '#rrggbb' of the rendered page pixel under pos."""
        if not self._image:
            return "#ffffff"
        iw, ih = self._image.width() or 1, self._image.height() or 1
        w, h = self.width() or 1, self.height() or 1
        ix = max(0, min(int(pos.x() * iw / w), iw - 1))
        iy = max(0, min(int(pos.y() * ih / h), ih - 1))
        return QColor(self._image.pixel(ix, iy)).name()


# ---------------------------------------------------------------------------
# Scrollable viewer
# ---------------------------------------------------------------------------

class PDFViewer(QScrollArea):
    page_changed = Signal(int)
    zoom_changed = Signal(float)
    text_edit_confirmed = Signal(QRectF, str, object)  # (norm_rect, new_text, formatting)
    text_selected = Signal(QRectF)                     # forwarded from PageWidget
    image_click_requested = Signal(float, float)       # forwarded from PageWidget
    image_draw_requested = Signal(QRectF)
    image_context_requested = Signal(float, float)    # right-click → check for image
    form_field_drawn = Signal(QRectF)
    annotation_moved = Signal(str, float, float)                        # forwarded from PageWidget
    form_element_moved = Signal(str, str, float, float, float, float)  # forwarded from PageWidget
    context_menu_requested = Signal(dict, int, int)                     # forwarded from PageWidget
    annotation_selected = Signal(dict)                                   # forwarded from PageWidget
    image_overlay_confirmed = Signal(int, int, float, float, float, float)
    image_overlay_cancelled = Signal()
    color_sampled = Signal(str)
    block_pick_requested = Signal(float, float)
    block_move_requested = Signal(float, float, float, float, float)
    ocr_overlay_changed = Signal(list)

    def __init__(
        self,
        renderer: Renderer,
        cache: PageCache,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._renderer = renderer
        self._cache = cache
        self._current_page = 0
        self._zoom = 1.0
        self._rotation = 0

        self._page_widget = PageWidget()
        self._page_widget.annotation_drawn.connect(self._on_annotation_drawn)
        self._page_widget.text_selected.connect(self.text_selected)
        self._page_widget.image_click_requested.connect(self.image_click_requested)
        self._page_widget.image_draw_requested.connect(self.image_draw_requested)
        self._page_widget.image_context_requested.connect(self.image_context_requested)
        self._page_widget.image_overlay_confirmed.connect(self.image_overlay_confirmed)
        self._page_widget.image_overlay_cancelled.connect(self.image_overlay_cancelled)
        self._page_widget.form_field_drawn.connect(
            lambda r: self.form_field_drawn.emit(r)
        )
        self._page_widget.annotation_moved.connect(self.annotation_moved)
        self._page_widget.annotation_selected.connect(self.annotation_selected)
        self._page_widget.form_element_moved.connect(self.form_element_moved)
        self._page_widget.context_menu_requested.connect(
            lambda ann, x, y: self.context_menu_requested.emit(ann, x, y)
        )
        self._page_widget.color_sampled.connect(self.color_sampled)
        self._page_widget.block_pick_requested.connect(self.block_pick_requested)
        self._page_widget.block_move_requested.connect(self.block_move_requested)
        self._page_widget.ocr_overlay_changed.connect(self.ocr_overlay_changed)
        self.setWidget(self._page_widget)
        self.setWidgetResizable(False)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("background: #404040;")

        # Navigate to next/prev page when the scrollbar reaches its limits
        self.verticalScrollBar().valueChanged.connect(self._on_vscroll_changed)
        self._scroll_at_limit = False  # debounce flag

    # ------------------------------------------------------------------

    def display_page(self, index: int, scroll_to_bottom: bool = False) -> None:
        if not self._renderer.is_open:
            return
        if index < 0 or index >= self._renderer.page_count:
            return
        self._current_page = index
        self._render_current()
        self.page_changed.emit(index)
        # Reposition scrollbar after render
        if scroll_to_bottom:
            self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())
        else:
            self.verticalScrollBar().setValue(0)

    def next_page(self) -> None:
        self.display_page(self._current_page + 1)

    def prev_page(self) -> None:
        self.display_page(self._current_page - 1)

    def set_zoom(self, zoom: float) -> None:
        self._zoom = max(0.1, min(zoom, 5.0))
        self._cache.invalidate(self._current_page)
        self._render_current()
        self.zoom_changed.emit(self._zoom)

    def highlight_search(self, rect: Optional[QRectF]) -> None:
        """Highlight a search match on the current page (normalized coords)."""
        self._page_widget.highlight_search(rect)

    def set_block_ghost(self, norm_rect: QRectF, *, start_dragging: bool = True) -> None:
        self._page_widget.set_block_ghost(norm_rect, start_dragging=start_dragging)

    def annotation_at_norm(self, norm_x: float, norm_y: float) -> Optional[dict]:
        return self._page_widget.annotation_at_norm(norm_x, norm_y)

    def set_form_overlays(self, overlays: list[dict]) -> None:
        self._page_widget.set_form_overlays(overlays)

    def set_ocr_overlay(self, items: list, opacity: float = 1.0, bg_white: bool = False) -> None:
        self._page_widget.set_ocr_overlay(items, opacity, bg_white)

    def clear_ocr_overlay(self) -> None:
        self._page_widget.clear_ocr_overlay()

    def zoom_in(self) -> None:
        self.set_zoom(self._zoom + 0.1)

    def zoom_out(self) -> None:
        self.set_zoom(self._zoom - 0.1)

    def zoom_fit_page(self) -> None:
        if not self._renderer.is_open:
            return
        w, h = self._renderer.get_page_size(self._current_page, zoom=1.0)
        vp = self.viewport()
        zoom_x = vp.width() / w if w else 1.0
        zoom_y = vp.height() / h if h else 1.0
        self.set_zoom(min(zoom_x, zoom_y))

    def zoom_fit_width(self) -> None:
        if not self._renderer.is_open:
            return
        w, _ = self._renderer.get_page_size(self._current_page, zoom=1.0)
        vp = self.viewport()
        self.set_zoom((vp.width() - 20) / w if w else 1.0)

    def set_tool(self, tool: str) -> None:
        self._page_widget.set_tool(tool)

    def add_annotation(self, ann: dict) -> None:
        self._page_widget.add_annotation(ann)

    def show_image_overlay(self, pil_img, norm_rect: QRectF) -> None:
        self._page_widget.show_image_overlay(pil_img, norm_rect)

    def clear_image_overlay(self) -> None:
        self._page_widget.clear_image_overlay()

    def refresh(self) -> None:
        self._cache.invalidate(self._current_page)
        self._render_current()

    def show_text_editor(
        self,
        norm_rect: QRectF,
        text: str,
        font_family: str = "Arial",
        font_size: float = 12.0,
        bold: bool = False,
        italic: bool = False,
        color: str = "#000000",
        underline: bool = False,
        letter_spacing: float = 0.0,
        bg_color: str = "",
    ) -> None:
        self._page_widget.show_text_editor(
            norm_rect, text, font_family, font_size, bold, italic, color,
            underline=underline, letter_spacing=letter_spacing, bg_color=bg_color,
        )

    @property
    def current_page(self) -> int:
        return self._current_page

    @property
    def zoom(self) -> float:
        return self._zoom

    def _render_current(self) -> None:
        key = (self._current_page, self._zoom, self._rotation)
        image = self._cache.get(key)
        if image is None:
            image = self._renderer.render_page(
                self._current_page, self._zoom, self._rotation
            )
            if image:
                self._cache.put(key, image)
        if image:
            self._page_widget.set_image(image)

    def _on_annotation_drawn(self, ann_type: str, rect: QRectF) -> None:
        pass  # handled by main_window

    def _on_vscroll_changed(self, value: int) -> None:
        """Navigate to next/prev page when scrollbar reaches its limits."""
        if self._scroll_at_limit:
            return
        vbar = self.verticalScrollBar()
        if value >= vbar.maximum() and vbar.maximum() > 0:
            if self._current_page < self._renderer.page_count - 1:
                self._scroll_at_limit = True
                self.display_page(self._current_page + 1, scroll_to_bottom=False)
                self._scroll_at_limit = False
        elif value == 0:
            if self._current_page > 0:
                self._scroll_at_limit = True
                self.display_page(self._current_page - 1, scroll_to_bottom=True)
                self._scroll_at_limit = False

    def wheelEvent(self, event: QWheelEvent) -> None:
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            if event.angleDelta().y() > 0:
                self.zoom_in()
            else:
                self.zoom_out()
            event.accept()
        else:
            vbar = self.verticalScrollBar()
            delta = event.angleDelta().y()
            # If scrolling down at the bottom → next page
            if delta < 0 and vbar.value() >= vbar.maximum():
                if self._current_page < self._renderer.page_count - 1:
                    self.display_page(self._current_page + 1, scroll_to_bottom=False)
                    event.accept()
                    return
            # If scrolling up at the top → previous page
            elif delta > 0 and vbar.value() == 0:
                if self._current_page > 0:
                    self.display_page(self._current_page - 1, scroll_to_bottom=True)
                    event.accept()
                    return
            super().wheelEvent(event)
