"""
Dialog for splitting (fractioning) a PDF into equal-size chunks.
"""
from __future__ import annotations

import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QSpinBox, QLabel, QFileDialog, QDialogButtonBox, QMessageBox,
)

from core.tools import PDFTools
from utils.i18n import _


class SplitDialog(QDialog):
    def __init__(self, input_path: str, page_count: int, parent=None) -> None:
        super().__init__(parent)
        self._input_path = input_path
        self._page_count = page_count
        self.setWindowTitle(_("Fractionner le PDF"))
        self.setMinimumWidth(380)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Info
        info = QLabel(
            _("Le PDF sera fractionné en plusieurs fichiers\n"
              "de N pages chacun, sur toute sa longueur.")
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        # Spinner
        form = QFormLayout()
        self._spin = QSpinBox()
        self._spin.setMinimum(1)
        self._spin.setMaximum(max(1, self._page_count))
        self._spin.setValue(1)
        self._spin.setFixedWidth(80)
        self._spin.valueChanged.connect(self._update_preview)
        form.addRow(_("Pages par fichier :"), self._spin)
        layout.addLayout(form)

        # Aperçu
        self._preview = QLabel()
        self._preview.setWordWrap(True)
        layout.addWidget(self._preview)
        self._update_preview()

        # Boutons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText(_("Fractionner…"))
        buttons.accepted.connect(self._do_split)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _update_preview(self) -> None:
        n = self._spin.value()
        import math
        chunks = math.ceil(self._page_count / n) if n > 0 else 0
        self._preview.setText(
            _("→ {chunks} fichier(s) de {n} page(s) "
              "(document : {total} pages au total)").format(
                chunks=chunks, n=n, total=self._page_count)
        )

    def _do_split(self) -> None:
        out_dir = QFileDialog.getExistingDirectory(
            self, _("Dossier de destination")
        )
        if not out_dir:
            return
        try:
            paths = PDFTools.split_by_chunk(
                self._input_path, out_dir, self._spin.value()
            )
            QMessageBox.information(
                self, _("Succès"),
                _("{n} fichier(s) créé(s) dans :\n{dir}").format(
                    n=len(paths), dir=out_dir)
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, _("Erreur"), str(e))
