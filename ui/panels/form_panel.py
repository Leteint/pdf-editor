"""
Form panel — affiche les champs AcroForm du PDF pour saisie et export JSON.
"""
from __future__ import annotations

import json
from typing import Optional

from PySide6.QtCore import Signal
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit, QCheckBox,
    QComboBox, QRadioButton, QButtonGroup, QHBoxLayout,
    QPushButton, QTextEdit, QLabel, QScrollArea, QApplication,
)

from core.forms import FormManager
from utils.i18n import _


class FormPanel(QWidget):
    save_requested = Signal()          # main_window sauvegarde le PDF après embed
    design_mode_toggled = Signal(bool) # True = activer le mode dessin de champs
    new_form_requested = Signal()      # créer un nouveau PDF vierge

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._manager: Optional[FormManager] = None
        # {field_name: (type_str, widget_or_group)}
        self._field_widgets: dict[str, tuple[str, object]] = {}
        self._build_ui()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(6, 6, 6, 6)

        btn_new = QPushButton(_("Nouveau formulaire vierge"))
        btn_new.clicked.connect(self.new_form_requested)
        root.addWidget(btn_new)

        self._btn_design = QPushButton(_("✏  Mode Design — Ajouter des champs"))
        self._btn_design.setCheckable(True)
        self._btn_design.setStyleSheet(
            "QPushButton:checked { background-color: #4a90d9; color: white; }"
        )
        self._btn_design.toggled.connect(
            lambda checked: self.design_mode_toggled.emit(checked)
        )
        root.addWidget(self._btn_design)

        self._no_form_label = QLabel(_("Aucun formulaire détecté dans ce PDF."))
        self._no_form_label.setStyleSheet("color: gray; font-size: 11px;")
        root.addWidget(self._no_form_label)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self._fields_container = QWidget()
        self._fields_layout = QFormLayout(self._fields_container)
        self._fields_layout.setContentsMargins(4, 4, 4, 4)
        scroll.setWidget(self._fields_container)
        root.addWidget(scroll)

        self._btn_save = QPushButton(_("Enregistrer et exporter JSON"))
        self._btn_save.clicked.connect(self._on_save)
        root.addWidget(self._btn_save)

        root.addWidget(QLabel(_("JSON embarqué :")))
        self._json_display = QTextEdit()
        self._json_display.setReadOnly(True)
        self._json_display.setMaximumHeight(140)
        self._json_display.setStyleSheet("font-family: monospace; font-size: 11px;")
        root.addWidget(self._json_display)

        self._status = QLabel("")
        self._status.setStyleSheet("color: green; font-size: 11px;")
        root.addWidget(self._status)

        self._set_form_visible(False)

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def load_form(self, manager: FormManager) -> None:
        self._manager = manager
        self._field_widgets = {}

        while self._fields_layout.rowCount():
            self._fields_layout.removeRow(0)

        if not manager.has_form():
            self._set_form_visible(False)
            self._json_display.clear()
            self._status.setText("")
            return

        self._set_form_visible(True)

        for defn in manager.get_field_definitions():
            name   = defn["name"]
            ftype  = defn["type"]
            value  = defn["value"]
            options = defn.get("options", [])

            if ftype == "text":
                widget = QLineEdit(str(value) if value else "")
                self._field_widgets[name] = ("text", widget)
                self._fields_layout.addRow(name, widget)

            elif ftype == "checkbox":
                widget = QCheckBox()
                widget.setChecked(bool(value))
                self._field_widgets[name] = ("checkbox", widget)
                self._fields_layout.addRow(name, widget)

            elif ftype == "dropdown":
                widget = QComboBox()
                for opt in options:
                    widget.addItem(opt)
                if value in options:
                    widget.setCurrentText(value)
                self._field_widgets[name] = ("dropdown", widget)
                self._fields_layout.addRow(name, widget)

            elif ftype in ("radio", "list"):
                group_widget = QWidget()
                group_layout = QHBoxLayout(group_widget)
                group_layout.setContentsMargins(0, 0, 0, 0)
                btn_group = QButtonGroup(group_widget)
                rb_style = self._radio_stylesheet()
                for opt in options:
                    rb = QRadioButton(opt)
                    rb.setStyleSheet(rb_style)
                    btn_group.addButton(rb)
                    if opt == value:
                        rb.setChecked(True)
                    group_layout.addWidget(rb)
                self._field_widgets[name] = ("radio", btn_group)
                self._fields_layout.addRow(name, group_widget)

        # JSON déjà embarqué ?
        existing = manager.get_embedded_json()
        if existing:
            self._json_display.setText(
                json.dumps(existing, ensure_ascii=False, indent=2)
            )
            self._status.setText(_("JSON précédemment embarqué."))

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def _on_save(self) -> None:
        if not self._manager:
            return

        values: dict = {}
        for name, (ftype, widget) in self._field_widgets.items():
            if ftype == "text":
                v = widget.text()                   # type: ignore[union-attr]
                values[name] = v
                self._manager.set_field(name, v)

            elif ftype == "checkbox":
                checked = widget.isChecked()        # type: ignore[union-attr]
                values[name] = checked
                self._manager.set_field(name, "true" if checked else "false")

            elif ftype == "dropdown":
                v = widget.currentText()            # type: ignore[union-attr]
                values[name] = v
                self._manager.set_field(name, v)

            elif ftype == "radio":
                selected = ""
                btn_group: QButtonGroup = widget     # type: ignore[assignment]
                checked_btn = btn_group.checkedButton()
                if checked_btn:
                    selected = checked_btn.text()
                values[name] = selected
                self._manager.set_field(name, selected)

        self._manager.embed_json(values)
        self._json_display.setText(
            json.dumps(values, ensure_ascii=False, indent=2)
        )
        self.save_requested.emit()
        self._status.setText(_("Données sauvegardées."))
        from PySide6.QtCore import QTimer
        QTimer.singleShot(3000, lambda: self._status.setText(""))

    # ------------------------------------------------------------------

    def exit_design_mode(self) -> None:
        """Called by main_window after a field is placed."""
        self._btn_design.setChecked(False)

    def set_design_mode(self, active: bool) -> None:
        """Sync the design button from an external trigger (e.g. toolbar)."""
        self._btn_design.setChecked(active)

    def _set_form_visible(self, visible: bool) -> None:
        self._no_form_label.setVisible(not visible)
        self._fields_container.setVisible(visible)
        self._btn_save.setVisible(visible)

    @staticmethod
    def _radio_stylesheet() -> str:
        """Retourne un stylesheet pour les QRadioButton adapté au thème courant."""
        app = QApplication.instance()
        palette = app.palette() if app else QPalette()
        # Texte clair = thème sombre ; texte sombre = thème clair
        text_lightness = palette.color(QPalette.ColorRole.WindowText).lightness()
        dark = text_lightness > 128

        dot_color   = "#ffffff" if dark else "#000000"
        border_idle = "#888888"
        border_checked = dot_color

        return (
            f"QRadioButton::indicator {{"
            f"  width: 14px; height: 14px;"
            f"  border-radius: 7px;"
            f"  border: 2px solid {border_idle};"
            f"  background-color: transparent;"
            f"}}"
            f"QRadioButton::indicator:checked {{"
            f"  background-color: {dot_color};"
            f"  border: 2px solid {border_checked};"
            f"}}"
        )
