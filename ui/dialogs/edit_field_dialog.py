"""
Dialogue de modification d'un champ de formulaire existant.
Permet de renommer le champ et de modifier ses options (dropdown/radio/checkbox).
"""
from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit,
    QDialogButtonBox, QVBoxLayout, QLabel,
)
from utils.i18n import _

_TYPE_LABELS = {
    "text":     "Input texte",
    "checkbox": "Case à cocher",
    "radio":    "Boutons radio",
    "dropdown": "Liste déroulante",
    "texte":    "Bloc de texte",
    "label":    "Label de texte",
}

_TYPES_WITH_OPTIONS = ("checkbox", "radio", "dropdown")


class EditFieldDialog(QDialog):
    """Pre-filled dialog for editing an existing form field."""

    def __init__(self, name: str, ftype: str, options: list[str], parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(_("Modifier le champ"))
        self.setMinimumWidth(380)
        self._ftype = ftype
        self._build_ui(name, ftype, options)

    def _build_ui(self, name: str, ftype: str, options: list[str]) -> None:
        layout = QVBoxLayout(self)
        form = QFormLayout()

        # Field name (editable)
        self._name_edit = QLineEdit(name)
        form.addRow(_("Identifiant :"), self._name_edit)

        # Type (read-only)
        type_label = QLabel(_TYPE_LABELS.get(ftype, ftype))
        form.addRow(_("Type :"), type_label)

        # Options (only for relevant types)
        self._options_edit: QLineEdit | None = None
        if ftype in _TYPES_WITH_OPTIONS:
            self._options_edit = QLineEdit(";".join(options))
            self._options_edit.setPlaceholderText("ex: Homme;Femme;Autre")
            form.addRow(_("Options (séparées par ; ) :"), self._options_edit)

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------

    def field_name(self) -> str:
        return self._name_edit.text().strip()

    def field_options(self) -> list[str]:
        if self._options_edit is None:
            return []
        return [o.strip() for o in self._options_edit.text().split(";") if o.strip()]
