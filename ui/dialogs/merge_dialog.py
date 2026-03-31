"""
Dialog for merging multiple PDF files.
"""
from __future__ import annotations

import os
from typing import Optional
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QListWidgetItem, QFileDialog,
    QDialogButtonBox, QLabel, QAbstractItemView,
)

from core.tools import PDFTools
from utils.i18n import _


class MergeDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(_("Fusionner des PDFs"))
        self.setMinimumSize(500, 400)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel(_("Fichiers à fusionner (glisser pour réordonner) :")))

        self._list = QListWidget()
        self._list.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        layout.addWidget(self._list)

        btn_row = QHBoxLayout()
        btn_add = QPushButton(_("Ajouter…"))
        btn_add.clicked.connect(self._add_files)
        btn_remove = QPushButton(_("Supprimer"))
        btn_remove.clicked.connect(self._remove_selected)
        btn_up = QPushButton(_("↑ Monter"))
        btn_up.clicked.connect(self._move_up)
        btn_down = QPushButton(_("↓ Descendre"))
        btn_down.clicked.connect(self._move_down)
        for b in (btn_add, btn_remove, btn_up, btn_down):
            btn_row.addWidget(b)
        layout.addLayout(btn_row)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._merge_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _add_files(self) -> None:
        paths, _filt = QFileDialog.getOpenFileNames(
            self, _("Choisir des PDFs"), "",
            "PDF (*.pdf)",
            options=QFileDialog.Option.DontUseNativeDialog,
        )
        for p in paths:
            item = QListWidgetItem(os.path.basename(p))
            item.setData(Qt.ItemDataRole.UserRole, p)
            item.setToolTip(p)
            self._list.addItem(item)

    def _remove_selected(self) -> None:
        for item in self._list.selectedItems():
            self._list.takeItem(self._list.row(item))

    def _move_up(self) -> None:
        row = self._list.currentRow()
        if row > 0:
            item = self._list.takeItem(row)
            self._list.insertItem(row - 1, item)
            self._list.setCurrentRow(row - 1)

    def _move_down(self) -> None:
        row = self._list.currentRow()
        if row < self._list.count() - 1:
            item = self._list.takeItem(row)
            self._list.insertItem(row + 1, item)
            self._list.setCurrentRow(row + 1)

    def _merge_and_accept(self) -> None:
        if self._list.count() < 2:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, _("Attention"), _("Ajoutez au moins 2 fichiers PDF."))
            return

        out_path, _filt = QFileDialog.getSaveFileName(
            self, _("Enregistrer le PDF fusionné"), "", _("PDF (*.pdf)")
        )
        if not out_path:
            return

        paths = [
            self._list.item(i).data(Qt.ItemDataRole.UserRole)
            for i in range(self._list.count())
        ]
        try:
            PDFTools.merge(paths, out_path)
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(self, _("Succès"), _("PDF fusionné :\n{path}").format(path=out_path))
            self.accept()
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, _("Erreur"), str(e))
