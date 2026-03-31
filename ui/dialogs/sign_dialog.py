"""
Dialog for signing a PDF with a PFX certificate.
"""
from __future__ import annotations

import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QPushButton, QLineEdit, QLabel, QFileDialog,
    QDialogButtonBox, QSpinBox, QMessageBox,
)

from core.signature import SignatureEngine
from utils.i18n import _


class SignDialog(QDialog):
    def __init__(self, input_path: str, page_count: int, parent=None) -> None:
        super().__init__(parent)
        self._input_path = input_path
        self._page_count = page_count
        self._engine = SignatureEngine()
        self.setWindowTitle(_("Signer le document"))
        self.setMinimumWidth(450)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        if not self._engine.is_available:
            layout.addWidget(QLabel(
                _(
                    "⚠️  pyHanko n'est pas installé.\n"
                    "Installez-le avec : pip install pyhanko pyhanko-certvalidator"
                )
            ))
            btn = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
            btn.rejected.connect(self.reject)
            layout.addWidget(btn)
            return

        form = QFormLayout()

        self._pfx_edit = QLineEdit()
        self._pfx_edit.setPlaceholderText(_("Chemin vers le fichier .pfx / .p12"))
        pfx_row = QHBoxLayout()
        pfx_row.addWidget(self._pfx_edit)
        btn_browse = QPushButton("…")
        btn_browse.setFixedWidth(30)
        btn_browse.clicked.connect(self._browse_pfx)
        pfx_row.addWidget(btn_browse)
        form.addRow(_("Certificat (.pfx) :"), pfx_row)

        self._pass_edit = QLineEdit()
        self._pass_edit.setEchoMode(QLineEdit.EchoMode.Password)
        form.addRow(_("Mot de passe :"), self._pass_edit)

        self._reason_edit = QLineEdit(_("Document signé électroniquement"))
        form.addRow(_("Raison :"), self._reason_edit)

        self._location_edit = QLineEdit()
        form.addRow(_("Lieu :"), self._location_edit)

        self._contact_edit = QLineEdit()
        form.addRow(_("Contact :"), self._contact_edit)

        self._page_spin = QSpinBox()
        self._page_spin.setMinimum(1)
        self._page_spin.setMaximum(self._page_count)
        form.addRow(_("Page :"), self._page_spin)

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._sign_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _browse_pfx(self) -> None:
        path, _filt = QFileDialog.getOpenFileName(
            self, _("Sélectionner le certificat"), "",
            _("Certificats (*.pfx *.p12);;Tous les fichiers (*)")
        )
        if path:
            self._pfx_edit.setText(path)

    def _sign_and_accept(self) -> None:
        pfx = self._pfx_edit.text().strip()
        if not pfx or not os.path.isfile(pfx):
            QMessageBox.warning(self, _("Erreur"), _("Sélectionnez un fichier certificat valide."))
            return

        out_path, _filt = QFileDialog.getSaveFileName(
            self, _("Enregistrer le PDF signé"), "", _("PDF (*.pdf)")
        )
        if not out_path:
            return

        try:
            self._engine.sign_with_pfx(
                input_path=self._input_path,
                output_path=out_path,
                pfx_path=pfx,
                pfx_password=self._pass_edit.text(),
                reason=self._reason_edit.text(),
                location=self._location_edit.text(),
                contact=self._contact_edit.text(),
                page=self._page_spin.value() - 1,
            )
            QMessageBox.information(self, _("Succès"), _("PDF signé sauvegardé :\n{path}").format(path=out_path))
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, _("Erreur"), str(e))
