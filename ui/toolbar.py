"""
Main toolbar and annotation toolbar.
"""
from __future__ import annotations

from typing import Optional
from PySide6.QtCore import Signal
from PySide6.QtGui import QAction, QIcon, QKeySequence
from PySide6.QtWidgets import (
    QToolBar, QWidget, QLabel, QSpinBox,
    QComboBox, QDoubleSpinBox, QSizePolicy,
)
from utils.i18n import _


class MainToolBar(QToolBar):
    # File actions
    action_open = Signal()
    action_save = Signal()
    action_save_as = Signal()
    # Navigation
    action_prev = Signal()
    action_next = Signal()
    action_goto = Signal(int)
    # Zoom
    action_zoom_in = Signal()
    action_zoom_out = Signal()
    action_zoom_fit = Signal()
    action_zoom_width = Signal()
    action_zoom_value = Signal(float)
    # View
    action_toggle_sidebar = Signal()
    action_fullscreen = Signal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(_("Barre principale"), parent)
        self.setMovable(False)
        self._build()

    def _build(self) -> None:
        self.setToolButtonStyle(
            __import__("PySide6.QtCore", fromlist=["Qt"]).Qt.ToolButtonStyle.ToolButtonTextUnderIcon
        )

        # Navigation
        self._btn_prev = QAction(_("◀ Préc."), self)
        self._btn_prev.setShortcut(QKeySequence("Left"))
        self._btn_prev.triggered.connect(self.action_prev.emit)
        self.addAction(self._btn_prev)

        self._page_spin = QSpinBox()
        self._page_spin.setMinimum(1)
        self._page_spin.setMaximum(9999)
        self._page_spin.setFixedWidth(90)
        self._page_spin.editingFinished.connect(
            lambda: self.action_goto.emit(self._page_spin.value() - 1)
        )
        self.addWidget(self._page_spin)

        self._page_label = QLabel(" / 0")
        self.addWidget(self._page_label)

        self._btn_next = QAction(_("Suiv. ▶"), self)
        self._btn_next.setShortcut(QKeySequence("Right"))
        self._btn_next.triggered.connect(self.action_next.emit)
        self.addAction(self._btn_next)

        self.addSeparator()

        # Zoom
        a = QAction("−", self)
        a.setShortcut(QKeySequence("Ctrl+-"))
        a.triggered.connect(self.action_zoom_out.emit)
        self.addAction(a)

        self._zoom_combo = QComboBox()
        presets = ["50%", "75%", "100%", "125%", "150%", "200%", _("Ajuster page"), _("Ajuster largeur")]
        self._zoom_combo.addItems(presets)
        self._zoom_combo.setCurrentText("100%")
        self._zoom_combo.setEditable(True)
        self._zoom_combo.setFixedWidth(130)
        self._zoom_combo.currentTextChanged.connect(self._on_zoom_text)
        self.addWidget(self._zoom_combo)

        a = QAction("+", self)
        a.setShortcut(QKeySequence("Ctrl+="))
        a.triggered.connect(self.action_zoom_in.emit)
        self.addAction(a)

        self.addSeparator()

        # View
        a = QAction("⊞ Sidebar", self)
        a.setCheckable(True)
        a.setChecked(True)
        a.setShortcut(QKeySequence("F4"))
        a.triggered.connect(self.action_toggle_sidebar.emit)
        self.addAction(a)

    def update_page_info(self, current: int, total: int) -> None:
        self._page_spin.blockSignals(True)
        self._page_spin.setMaximum(total)
        self._page_spin.setValue(current + 1)
        self._page_spin.blockSignals(False)
        self._page_label.setText(f" / {total}")

    def update_zoom(self, zoom: float) -> None:
        self._zoom_combo.blockSignals(True)
        self._zoom_combo.setCurrentText(f"{int(zoom * 100)}%")
        self._zoom_combo.blockSignals(False)

    def _on_zoom_text(self, text: str) -> None:
        text = text.strip()
        if text == _("Ajuster page"):
            self.action_zoom_fit.emit()
        elif text == _("Ajuster largeur"):
            self.action_zoom_width.emit()
        else:
            try:
                val = float(text.replace("%", "").strip()) / 100.0
                if val > 0:
                    self.action_zoom_value.emit(val)
            except ValueError:
                pass


class PagesToolBar(QToolBar):
    """Secondary toolbar: page management + form design mode toggle."""
    action_merge         = Signal()
    action_split         = Signal()
    action_delete_page   = Signal()
    action_form_design   = Signal(bool)   # checked state
    action_insert_image  = Signal()
    action_insert_text   = Signal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(_("Pages & Formulaire"), parent)
        self.setMovable(False)
        self._build()

    def _build(self) -> None:
        a = QAction(_("⊕ Réorganiser/Fusionner"), self)
        a.setStatusTip(_("Réorganiser/Fusionner les pages…"))
        a.triggered.connect(self.action_merge.emit)
        self.addAction(a)

        a = QAction(_("✂ Fractionner"), self)
        a.setStatusTip(_("Fractionner ce PDF…"))
        a.triggered.connect(self.action_split.emit)
        self.addAction(a)

        a = QAction(_("🗑 Suppr. page"), self)
        a.setStatusTip(_("Supprimer la page courante (Delete)"))
        a.triggered.connect(self.action_delete_page.emit)
        self.addAction(a)

        self.addSeparator()

        a = QAction(_("🖼 Insérer image"), self)
        a.setStatusTip(_("Dessiner une zone pour insérer une image dans le PDF"))
        a.triggered.connect(self.action_insert_image.emit)
        self.addAction(a)

        a = QAction(_("📝 Insérer texte"), self)
        a.setStatusTip(_("Dessiner une zone pour insérer un bloc de texte dans le PDF"))
        a.triggered.connect(self.action_insert_text.emit)
        self.addAction(a)

        self.addSeparator()

        self._act_design = QAction(_("✏ Mode Design"), self)
        self._act_design.setCheckable(True)
        self._act_design.setStatusTip(_("Activer/désactiver le mode design de formulaire"))
        self._act_design.triggered.connect(
            lambda checked: self.action_form_design.emit(checked)
        )
        self.addAction(self._act_design)

    def set_design_mode(self, active: bool) -> None:
        """Sync the toolbar button without firing action_form_design."""
        self._act_design.setChecked(active)


class AnnotationToolBar(QToolBar):
    tool_selected = Signal(str)  # select | highlight | underline | draw | comment | erase

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(_("Annotations"), parent)
        self.setMovable(False)
        self._build()

    def _build(self) -> None:
        tools = [
            (_("Sélection"), "select", "S"),
            (_("Modifier texte"), "text_edit", "T"),
            (_("Surligner"), "highlight", "H"),
            (_("Souligner"), "underline", "U"),
            (_("Commentaire"), "comment", "C"),
            (_("Image"), "image", "I"),
            (_("Effacer"), "erase", "E"),
        ]
        for label, tool_id, shortcut in tools:
            a = QAction(label, self)
            a.setCheckable(True)
            a.setShortcut(QKeySequence(shortcut))
            a.setData(tool_id)
            a.triggered.connect(lambda checked, t=tool_id: self._select_tool(t))
            self.addAction(a)
        # Select by default
        self.actions()[0].setChecked(True)

    def _select_tool(self, tool: str) -> None:
        for action in self.actions():
            action.setChecked(action.data() == tool)
        self.tool_selected.emit(tool)
