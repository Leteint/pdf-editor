"""
License activation dialog — shown at first launch or when license is invalid.
"""
from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QDialogButtonBox, QMessageBox,
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont

from utils.i18n import _


class _ValidateThread(QThread):
    """Run license check in background to avoid freezing the UI."""
    result_ready = Signal(object)   # LicenseResult

    def __init__(self, key: str) -> None:
        super().__init__()
        self._key = key

    def run(self) -> None:
        from utils.license import check_license
        result = check_license(self._key)
        self.result_ready.emit(result)


class LicenseDialog(QDialog):
    """
    Shown when no valid license is found.
    User enters their license key → validated online.
    """

    def __init__(self, parent=None, message: str = "") -> None:
        super().__init__(parent)
        self.setWindowTitle(_("Activation de PDF Editor"))
        self.setMinimumWidth(480)
        self.setWindowFlags(
            self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint
        )
        self._thread: _ValidateThread | None = None
        self._build(message)

    def _build(self, message: str) -> None:
        lay = QVBoxLayout(self)
        lay.setSpacing(14)

        # ── Title ────────────────────────────────────────────────────────
        title = QLabel("🔑  " + _("Activation de PDF Editor"))
        font = QFont()
        font.setPointSize(13)
        font.setBold(True)
        title.setFont(font)
        lay.addWidget(title)

        # ── Message (reason for showing dialog) ──────────────────────────
        if message:
            msg_lbl = QLabel(message)
            msg_lbl.setWordWrap(True)
            msg_lbl.setStyleSheet("color: #e07050;")
            lay.addWidget(msg_lbl)

        # ── Explanation ──────────────────────────────────────────────────
        info = QLabel(_(
            "Veuillez entrer votre clé de licence reçue par email après l'achat.\n"
            "Format : XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"
        ))
        info.setWordWrap(True)
        lay.addWidget(info)

        # ── Key input ────────────────────────────────────────────────────
        self._key_edit = QLineEdit()
        self._key_edit.setPlaceholderText("XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX")
        self._key_edit.setFont(QFont("Consolas", 11))
        self._key_edit.textChanged.connect(self._on_text_changed)
        lay.addWidget(self._key_edit)

        # ── Buy link ─────────────────────────────────────────────────────
        buy_lbl = QLabel(
            _("Pas encore de licence ? ")
            + "<a href='https://pdfeditor.lemonsqueezy.com'>"
            + _("Acheter PDF Editor")
            + "</a>"
        )
        buy_lbl.setOpenExternalLinks(True)
        buy_lbl.setTextFormat(Qt.TextFormat.RichText)
        lay.addWidget(buy_lbl)

        # ── Status label ─────────────────────────────────────────────────
        self._status_lbl = QLabel("")
        self._status_lbl.setWordWrap(True)
        lay.addWidget(self._status_lbl)

        # ── Buttons ──────────────────────────────────────────────────────
        btn_row = QHBoxLayout()
        self._btn_activate = QPushButton("✅  " + _("Activer"))
        self._btn_activate.setEnabled(False)
        self._btn_activate.setDefault(True)
        self._btn_activate.clicked.connect(self._activate)

        btn_quit = QPushButton(_("Quitter"))
        btn_quit.clicked.connect(self.reject)

        btn_row.addStretch()
        btn_row.addWidget(btn_quit)
        btn_row.addWidget(self._btn_activate)
        lay.addLayout(btn_row)

    # ── Slots ─────────────────────────────────────────────────────────────

    def _on_text_changed(self, text: str) -> None:
        # Enable button only if input looks like a UUID key
        cleaned = text.strip()
        self._btn_activate.setEnabled(len(cleaned) >= 16)

    def _activate(self) -> None:
        key = self._key_edit.text().strip()
        if not key:
            return

        self._btn_activate.setEnabled(False)
        self._btn_activate.setText(_("Vérification…"))
        self._status_lbl.setText("⏳ " + _("Connexion à Lemon Squeezy…"))
        self._status_lbl.setStyleSheet("color: #aaa;")

        self._thread = _ValidateThread(key)
        self._thread.result_ready.connect(self._on_result)
        self._thread.start()

    def _on_result(self, result) -> None:
        self._btn_activate.setText("✅  " + _("Activer"))

        if result.valid:
            color = "#f0a800" if result.offline else "#60c060"
            self._status_lbl.setStyleSheet(f"color: {color};")
            self._status_lbl.setText("✅  " + result.reason)
            self._btn_activate.setEnabled(False)
            # Auto-close after short delay
            from PySide6.QtCore import QTimer
            QTimer.singleShot(1200, self.accept)
        else:
            self._status_lbl.setStyleSheet("color: #e07050;")
            self._status_lbl.setText("❌  " + result.reason)
            self._btn_activate.setEnabled(True)
