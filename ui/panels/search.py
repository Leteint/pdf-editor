"""
Search panel — full text search across the PDF.
"""
from __future__ import annotations

from typing import Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QListWidget, QListWidgetItem, QLabel,
    QCheckBox,
)
import pdfplumber
from utils.i18n import _


class SearchPanel(QWidget):
    result_selected = Signal(int, str)  # page_index, matched_text
    close_requested = Signal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._pdf_path: Optional[str] = None
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)

        layout.addWidget(QLabel(_("Rechercher dans le document :")))

        search_row = QHBoxLayout()
        self._input = QLineEdit()
        self._input.setPlaceholderText(_("Terme de recherche…"))
        self._input.returnPressed.connect(self._do_search)
        search_row.addWidget(self._input)

        btn_search = QPushButton(_("Chercher"))
        btn_search.clicked.connect(self._do_search)
        search_row.addWidget(btn_search)
        layout.addLayout(search_row)

        self._cb_case = QCheckBox(_("Respecter la casse"))
        layout.addWidget(self._cb_case)

        self._status_label = QLabel("")
        self._status_label.setStyleSheet("color: gray; font-size: 11px;")
        layout.addWidget(self._status_label)

        self._result_list = QListWidget()
        self._result_list.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self._result_list)

        layout.addSpacing(4)
        btn_close = QPushButton(_("Fermer"))
        btn_close.clicked.connect(self.close_requested)
        layout.addWidget(btn_close)

    def set_document(self, pdf_path: str) -> None:
        self._pdf_path = pdf_path
        self._result_list.clear()
        self._status_label.setText("")

    def _do_search(self) -> None:
        query = self._input.text().strip()
        if not query or not self._pdf_path:
            return

        self._result_list.clear()
        self._status_label.setText(_("Recherche en cours…"))

        case_sensitive = self._cb_case.isChecked()
        count = 0

        try:
            with pdfplumber.open(self._pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    text = page.extract_text() or ""
                    compare_text = text if case_sensitive else text.lower()
                    compare_query = query if case_sensitive else query.lower()

                    if compare_query in compare_text:
                        # Find each occurrence and show context
                        lines = text.split("\n")
                        for line in lines:
                            compare_line = line if case_sensitive else line.lower()
                            if compare_query in compare_line:
                                item = QListWidgetItem(f"Page {page_num + 1}: {line.strip()[:80]}")
                                item.setData(Qt.ItemDataRole.UserRole, (page_num, line.strip()))
                                self._result_list.addItem(item)
                                count += 1
        except Exception as e:
            self._status_label.setText(_("Erreur : {err}").format(err=e))
            return

        self._status_label.setText(
            _("{n} occurrence(s) trouvée(s).").format(n=count) if count else _("Aucun résultat.")
        )

    @property
    def current_query(self) -> str:
        return self._input.text().strip()

    @property
    def is_case_sensitive(self) -> bool:
        return self._cb_case.isChecked()

    def focus_search(self) -> None:
        """Show the search field focused and ready to type."""
        self._input.setFocus()
        self._input.selectAll()

    def _on_item_double_clicked(self, item: QListWidgetItem) -> None:
        data = item.data(Qt.ItemDataRole.UserRole)
        if data:
            page_num, text = data
            self.result_selected.emit(page_num, text)
