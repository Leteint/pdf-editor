"""
Left accordion tool panel.
Replaces the top AnnotationToolBar + AnnotationPropertiesBar.
"""
from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QColor, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFrame, QDoubleSpinBox, QColorDialog,
    QScrollArea, QSizePolicy,
)
from utils.i18n import _

_PRESETS = [
    ("#FFFF00", "Jaune"),
    ("#FF6B6B", "Rouge"),
    ("#6BFF6B", "Vert"),
    ("#6BB5FF", "Bleu"),
    ("#FF9900", "Orange"),
    ("#CC66FF", "Violet"),
]

_TOOLS = [
    ("highlight",   "Surligner",        "H"),
    ("underline",   "Souligner",        "U"),
    ("comment",     "Commentaire",      "C"),
    ("erase",       "Effacer",          "E"),
    ("move_block",  "Déplacer texte",   "M"),
]

_PDF_ACTIONS = [
    ("insert_image",  "🖼",  "Insérer une image…"),
    ("insert_text",   "📝",  "Insérer un bloc de texte…"),
    ("move_block",    "↔",  "Déplacer un bloc de texte"),
    ("organize",      "⊕",  "Réorganiser/Fusionner…"),
    ("split",         "✂",  "Fractionner…"),
    ("delete_page",   "🗑",  "Supprimer la page courante"),
    ("extract_text",  "📄",  "Extraire le texte…"),
    ("extract_img",   "🖼",  "Extraire les images…"),
    ("metadata",      "ℹ",  "Métadonnées…"),
    ("hf",            "☰",  "En-têtes / pieds de page…"),
    ("watermark",     "◈",  "Filigrane…"),
    ("stamp_text",    "🖊",  "Tampon texte…"),
    ("stamp_image",   "🖼",  "Tampon image…"),
    ("compress",      "⚡",  "Compresser le PDF"),
    ("protect",       "🔒",  "Protéger par mot de passe…"),
    ("unlock",        "🔓",  "Supprimer la protection…"),
    ("sign",          "✍",  "Signer le document…"),
    ("verify_sigs",   "🔎",  "Vérifier les signatures…"),
    ("rotate_cw",     "↻",  "Tourner la page (+90°)"),
    ("rotate_ccw",    "↺",  "Tourner la page (-90°)"),
    ("search",        "🔍",  "Recherche…"),
    ("ocr",           "🔤",  "Reconnaissance de caractères (OCR)…"),
]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

class _ColorSwatch(QPushButton):
    color_picked = Signal(str)

    def __init__(self, color: str, tooltip: str, parent=None) -> None:
        super().__init__(parent)
        self._color = color
        self._custom = (color == "__custom__")
        self.setFixedSize(22, 22)
        self.setToolTip(tooltip)
        self._refresh()
        self.clicked.connect(self._pick)

    def _refresh(self) -> None:
        c = self._color if not self._custom else "#888888"
        self.setStyleSheet(
            f"background:{c}; border:1px solid #666; border-radius:3px;"
        )

    def _pick(self) -> None:
        if self._custom:
            picked = QColorDialog.getColor(parent=self)
            if picked.isValid():
                self._color = picked.name()
                self._custom = False
                self._refresh()
                self.color_picked.emit(self._color)
        else:
            self.color_picked.emit(self._color)

    def set_color(self, color: str) -> None:
        self._color = color
        self._custom = False
        self._refresh()


class CollapsibleSection(QWidget):
    """A titled section that can be collapsed/expanded."""

    def __init__(self, title: str, expanded: bool = True,
                 parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._title = title
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 2)
        root.setSpacing(0)

        self._toggle = QPushButton()
        self._toggle.setCheckable(True)
        self._toggle.setChecked(expanded)
        self._toggle.setStyleSheet(
            "QPushButton {"
            "  text-align: left; padding: 5px 8px;"
            "  font-weight: bold; border: none;"
            "  border-bottom: 1px solid #555;"
            "}"
            "QPushButton:checked { background: #3a3a4e; }"
            "QPushButton:hover   { background: #444; }"
        )
        self._toggle.toggled.connect(self._on_toggle)
        root.addWidget(self._toggle)

        self._body = QWidget()
        self._body_layout = QVBoxLayout(self._body)
        self._body_layout.setContentsMargins(6, 4, 6, 6)
        self._body_layout.setSpacing(4)
        self._body.setVisible(expanded)
        root.addWidget(self._body)

        self._on_toggle(expanded)  # set initial arrow

    def _on_toggle(self, checked: bool) -> None:
        arrow = "▼" if checked else "▶"
        self._toggle.setText(f"{arrow}  {self._title}")
        self._body.setVisible(checked)

    def add_widget(self, w: QWidget) -> None:
        self._body_layout.addWidget(w)

    def add_layout(self, lay) -> None:
        self._body_layout.addLayout(lay)


# ---------------------------------------------------------------------------
# Main panel
# ---------------------------------------------------------------------------

class LeftToolPanel(QWidget):
    """Accordion tool panel — emits the same signals as the old toolbars."""
    tool_selected        = Signal(str)    # "highlight"|"underline"|"comment"|"erase"|"select"
    color_changed        = Signal(str)    # hex
    stroke_width_changed = Signal(float)
    action_triggered     = Signal(str)    # action id from _PDF_ACTIONS

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._current_color = "#FFFF00"
        self._tool_buttons: dict[str, QPushButton] = {}
        self._build()

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def _build(self) -> None:
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        container = QWidget()
        root = QVBoxLayout(container)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ---- Annotations section ----------------------------------------
        sec = CollapsibleSection(_("✏  Annotations"), expanded=False)

        for tool_id, label, shortcut in _TOOLS:
            btn = QPushButton(_(label) + (f"  [{shortcut}]" if shortcut else ""))
            btn.setCheckable(True)
            btn.setStyleSheet(
                "QPushButton { padding: 6px 8px; text-align: left; border-radius: 3px; }"
                "QPushButton:checked { background: #4a90d9; color: white; }"
                "QPushButton:hover:!checked { background: #555; }"
            )
            btn.clicked.connect(
                lambda checked, t=tool_id: self._on_tool_click(t, checked)
            )
            if shortcut:
                sc = QShortcut(QKeySequence(shortcut), btn)
                sc.setContext(Qt.ShortcutContext.ApplicationShortcut)
                sc.activated.connect(lambda t=tool_id: self._on_shortcut(t))
            self._tool_buttons[tool_id] = btn
            sec.add_widget(btn)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #555; margin: 2px 0;")
        sec.add_widget(sep)

        # Color row
        sec.add_widget(QLabel(_("Couleur :")))
        row_colors = QHBoxLayout()
        row_colors.setSpacing(3)
        for hex_c, name in _PRESETS:
            sw = _ColorSwatch(hex_c, _(name))
            sw.color_picked.connect(self._on_color)
            row_colors.addWidget(sw)
        custom_sw = _ColorSwatch("__custom__", _("Personnalisé"))
        custom_sw.color_picked.connect(self._on_color)
        row_colors.addWidget(custom_sw)
        row_colors.addStretch()
        sec.add_layout(row_colors)

        # Stroke row
        row_stroke = QHBoxLayout()
        row_stroke.addWidget(QLabel(_("Épaisseur :")))
        self._stroke_spin = QDoubleSpinBox()
        self._stroke_spin.setRange(0.5, 10.0)
        self._stroke_spin.setValue(2.0)
        self._stroke_spin.setSingleStep(0.5)
        self._stroke_spin.setFixedWidth(96)
        self._stroke_spin.valueChanged.connect(self.stroke_width_changed.emit)
        row_stroke.addWidget(self._stroke_spin)
        row_stroke.addStretch()
        sec.add_layout(row_stroke)

        root.addWidget(sec)

        # ---- Tips section -----------------------------------------------
        sec2 = CollapsibleSection(_("💡 Raccourcis"), expanded=False)
        for tip in [
            _("Double-clic → modifier texte"),
            _("Clic droit → menu contextuel"),
            _("H  Surligner"),
            _("C  Commentaire"),
            _("E  Effacer"),
            _("M  Déplacer texte"),
        ]:
            lbl = QLabel(tip)
            lbl.setStyleSheet("color: #aaa; font-size: 11px;")
            lbl.setWordWrap(True)
            sec2.add_widget(lbl)
        root.addWidget(sec2)

        # ---- PDF tools section ------------------------------------------
        sec3 = CollapsibleSection(_("🛠  Outils"), expanded=True)
        for action_id, icon, label in _PDF_ACTIONS:
            btn = QPushButton(f"{icon}  {_(label)}")
            btn.setStyleSheet(
                "QPushButton { padding: 6px 8px; text-align: left;"
                " border-radius: 3px; }"
                "QPushButton:hover { background: #555; }"
            )
            btn.clicked.connect(
                lambda _checked=False, aid=action_id: self.action_triggered.emit(aid)
            )
            sec3.add_widget(btn)
        root.addWidget(sec3)

        root.addStretch()
        scroll.setWidget(container)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def _on_shortcut(self, tool_id: str) -> None:
        """Toggle tool on/off via keyboard shortcut."""
        btn = self._tool_buttons.get(tool_id)
        if btn is None:
            return
        new_state = not btn.isChecked()
        self._on_tool_click(tool_id, new_state)
        btn.setChecked(new_state)

    def _on_tool_click(self, tool_id: str, checked: bool) -> None:
        for tid, btn in self._tool_buttons.items():
            if tid != tool_id:
                btn.setChecked(False)
        self.tool_selected.emit(tool_id if checked else "select")

    def _on_color(self, color: str) -> None:
        self._current_color = color
        self.color_changed.emit(color)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def deselect_all(self) -> None:
        for btn in self._tool_buttons.values():
            btn.setChecked(False)

    def select_tool(self, tool_id: str) -> None:
        for tid, btn in self._tool_buttons.items():
            btn.setChecked(tid == tool_id)

    @property
    def current_color(self) -> str:
        return self._current_color

    @property
    def current_stroke_width(self) -> float:
        return self._stroke_spin.value()
