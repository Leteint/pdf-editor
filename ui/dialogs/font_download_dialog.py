"""
Dialog proposing to download a missing font from Google Fonts.
"""
from __future__ import annotations

from PySide6.QtCore import Qt, QThread, Signal, QObject
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QProgressBar,
    QDialogButtonBox, QPushButton, QHBoxLayout,
)


class _DownloadWorker(QObject):
    progress = Signal(int)
    finished = Signal(bool)

    def __init__(self, family: str) -> None:
        super().__init__()
        self._family = family

    def run(self) -> None:
        from utils.font_manager import download_font
        ok = download_font(self._family, progress_cb=self.progress.emit)
        self.finished.emit(ok)


class FontDownloadDialog(QDialog):
    """
    Shown when a PDF uses a font that is not installed on the system.
    Proposes downloading a free equivalent from Google Fonts.
    """

    def __init__(
        self,
        pdf_font_name: str,
        suggested_family: str,
        note: str,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._family = suggested_family
        self._success = False
        self.setWindowTitle("Police manquante")
        self.setMinimumWidth(420)
        self._build_ui(pdf_font_name, suggested_family, note)

    def _build_ui(self, pdf_font_name: str, suggested: str, note: str) -> None:
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel(
            f"<b>Police du document :</b> {pdf_font_name}<br>"
            f"<b>Équivalent libre proposé :</b> {suggested}<br><br>"
            f"<i>{note}</i><br><br>"
            "Cette police sera téléchargée depuis <b>Google Fonts</b> (licence OFL/Apache — libre de droits).<br>"
            "Elle sera enregistrée localement et utilisée automatiquement à l'avenir."
        ))
        layout.addSpacing(8)

        self._progress = QProgressBar()
        self._progress.setRange(0, 100)
        self._progress.setVisible(False)
        layout.addWidget(self._progress)

        self._status_lbl = QLabel("")
        self._status_lbl.setStyleSheet("color:gray; font-size:11px;")
        layout.addWidget(self._status_lbl)

        btn_row = QHBoxLayout()
        self._btn_download = QPushButton("Télécharger la police")
        self._btn_download.setDefault(True)
        self._btn_download.clicked.connect(self._start_download)
        btn_row.addWidget(self._btn_download)

        btn_skip = QPushButton("Ignorer (utiliser Arial)")
        btn_skip.clicked.connect(self.reject)
        btn_row.addWidget(btn_skip)
        layout.addLayout(btn_row)

    def _start_download(self) -> None:
        self._btn_download.setEnabled(False)
        self._progress.setVisible(True)
        self._status_lbl.setText("Téléchargement en cours…")

        self._worker = _DownloadWorker(self._family)
        self._thread = QThread()
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.progress.connect(self._progress.setValue)
        self._worker.finished.connect(self._on_finished)
        self._worker.finished.connect(self._thread.quit)
        self._thread.start()

    def _on_finished(self, ok: bool) -> None:
        self._success = ok
        if ok:
            self._status_lbl.setText("Police installée avec succès !")
            self._progress.setValue(100)
            from PySide6.QtCore import QTimer
            QTimer.singleShot(1000, self.accept)
        else:
            self._status_lbl.setText(
                "Échec du téléchargement. Vérifiez votre connexion internet."
            )
            self._btn_download.setEnabled(True)

    @property
    def success(self) -> bool:
        return self._success
