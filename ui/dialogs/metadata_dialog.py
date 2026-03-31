"""
Dialog for editing PDF metadata (title, author, subject, keywords, creator).
"""
from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog, QFormLayout, QVBoxLayout, QLineEdit,
    QDialogButtonBox, QLabel,
)
from utils.i18n import _


class MetadataDialog(QDialog):
    def __init__(self, meta: dict, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(_("Métadonnées du document"))
        self.setMinimumWidth(420)
        self._build(meta)

    def _build(self, meta: dict) -> None:
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel(_("Informations enregistrées dans le fichier PDF :")))

        form = QFormLayout()
        self._title    = QLineEdit(meta.get("title",    ""))
        self._author   = QLineEdit(meta.get("author",   ""))
        self._subject  = QLineEdit(meta.get("subject",  ""))
        self._keywords = QLineEdit(meta.get("keywords", ""))
        self._creator  = QLineEdit(meta.get("creator",  ""))

        form.addRow(_("Titre :"),          self._title)
        form.addRow(_("Auteur :"),         self._author)
        form.addRow(_("Sujet :"),          self._subject)
        form.addRow(_("Mots-clés :"),      self._keywords)
        form.addRow(_("Application :"),    self._creator)
        layout.addLayout(form)

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    @property
    def metadata(self) -> dict:
        return {
            "title":    self._title.text().strip(),
            "author":   self._author.text().strip(),
            "subject":  self._subject.text().strip(),
            "keywords": self._keywords.text().strip(),
            "creator":  self._creator.text().strip(),
        }
