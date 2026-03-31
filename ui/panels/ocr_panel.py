"""
OCR panel — run OCR on current page and display/export result.
"""
from __future__ import annotations

from typing import Optional
from PySide6.QtCore import Qt, Signal, QThread, QObject
from PySide6.QtGui import QImage
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTextEdit, QLabel, QComboBox, QFileDialog,
    QProgressBar, QMessageBox, QSlider,
)

from core.ocr import OCREngine
from utils.i18n import _


class OCRWorker(QObject):
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, engine: OCREngine, image: QImage, lang: str) -> None:
        super().__init__()
        self._engine = engine
        self._image = image
        self._lang = lang

    def run(self) -> None:
        try:
            text = self._engine.run_page(self._image, self._lang)
            self.finished.emit(text)
        except Exception as e:
            self.error.emit(str(e))


class OCROverlayWorker(QObject):
    """Run line-level OCR and emit results for PDF overlay."""
    finished = Signal(list, int, int)  # lines, img_w, img_h
    error = Signal(str)

    def __init__(self, engine: OCREngine, image: QImage, lang: str) -> None:
        super().__init__()
        self._engine = engine
        self._image = image
        self._lang = lang

    def run(self) -> None:
        try:
            lines = self._engine.run_page_lines(self._image, self._lang)
            self.finished.emit(lines, self._image.width(), self._image.height())
        except Exception as e:
            self.error.emit(str(e))


class OCRPanel(QWidget):
    request_current_image   = Signal()                  # asks main window for current page image
    overlay_requested       = Signal(list, int, int, bool, float)  # write to PDF
    ocr_lines_ready         = Signal(list, int, int)    # preview: lines, img_w, img_h
    preview_settings_changed = Signal(float, bool)      # opacity, bg_white
    close_requested         = Signal()                  # user clicked "Fermer"

    def __init__(self, engine: OCREngine, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._engine = engine
        self._thread: Optional[QThread] = None
        self._current_image: Optional[QImage] = None
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)

        if not self._engine.is_available:
            lbl = QLabel(
                _(
                    "⚠️  Tesseract OCR non installé.\n\n"
                    "Téléchargez-le ici :\n"
                    "https://github.com/UB-Mannheim/tesseract/wiki\n\n"
                    "Puis redémarrez l'application."
                )
            )
            lbl.setWordWrap(True)
            layout.addWidget(lbl)
            return

        top_row = QHBoxLayout()
        top_row.addWidget(QLabel(_("Langue :")))
        self._lang_combo = QComboBox()
        langs = OCREngine.available_languages()
        self._lang_combo.addItems(langs if langs else ["fra", "eng"])
        if "fra" in langs:
            self._lang_combo.setCurrentText("fra")
        top_row.addWidget(self._lang_combo)
        layout.addLayout(top_row)

        self._btn_run = QPushButton(_("Lancer l'OCR sur la page courante"))
        self._btn_run.clicked.connect(self._run_ocr)
        layout.addWidget(self._btn_run)

        self._progress = QProgressBar()
        self._progress.setRange(0, 0)  # indeterminate
        self._progress.setVisible(False)
        layout.addWidget(self._progress)

        layout.addWidget(QLabel(_("Texte extrait :")))
        self._text_edit = QTextEdit()
        self._text_edit.setReadOnly(False)
        layout.addWidget(self._text_edit)

        btn_row = QHBoxLayout()
        btn_copy = QPushButton(_("Copier"))
        btn_copy.clicked.connect(self._copy_text)
        btn_export = QPushButton(_("Exporter .txt"))
        btn_export.clicked.connect(self._export_text)
        btn_row.addWidget(btn_copy)
        btn_row.addWidget(btn_export)
        layout.addLayout(btn_row)

        layout.addSpacing(6)

        opacity_row = QHBoxLayout()
        opacity_row.addWidget(QLabel(_("Opacité :")))
        self._opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self._opacity_slider.setRange(10, 100)
        self._opacity_slider.setValue(100)
        self._opacity_slider.setTickInterval(10)
        self._opacity_val_label = QLabel("100%")
        self._opacity_val_label.setFixedWidth(38)
        self._opacity_slider.valueChanged.connect(self._on_preview_setting_changed)
        self._opacity_slider.valueChanged.connect(
            lambda v: self._opacity_val_label.setText(f"{v}%")
        )
        opacity_row.addWidget(self._opacity_slider)
        opacity_row.addWidget(self._opacity_val_label)
        layout.addLayout(opacity_row)

        self._btn_overlay = QPushButton(_("Incruster le texte OCR dans le PDF"))
        self._btn_overlay.clicked.connect(self._run_ocr_overlay)
        layout.addWidget(self._btn_overlay)

        layout.addSpacing(4)
        btn_close = QPushButton(_("Fermer"))
        btn_close.clicked.connect(self.close_requested)
        layout.addWidget(btn_close)

    def set_image(self, image: QImage) -> None:
        self._current_image = image

    def _run_ocr(self) -> None:
        if self._current_image is None:
            self.request_current_image.emit()
            return
        self._start_ocr(self._current_image)

    def _start_ocr(self, image: QImage) -> None:
        if not hasattr(self, "_btn_run"):
            return  # Tesseract unavailable — UI not fully built
        lang = self._lang_combo.currentText() if hasattr(self, "_lang_combo") else "fra"
        self._btn_run.setEnabled(False)
        self._progress.setVisible(True)

        self._worker = OCRWorker(self._engine, image, lang)
        self._thread = QThread()
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(self._on_ocr_done)
        self._worker.error.connect(self._on_ocr_error)
        self._worker.finished.connect(self._thread.quit)
        self._worker.error.connect(self._thread.quit)
        self._thread.start()

    def _on_ocr_done(self, text: str) -> None:
        self._text_edit.setPlainText(text)
        self._btn_run.setEnabled(True)
        self._progress.setVisible(False)

    def _on_ocr_error(self, msg: str) -> None:
        self._btn_run.setEnabled(True)
        self._progress.setVisible(False)
        QMessageBox.critical(self, _("Erreur OCR"), msg)

    def _run_ocr_overlay(self) -> None:
        if self._current_image is None:
            self.request_current_image.emit()
            # Will be retried once image is provided via set_image + signal chain
            return
        self._btn_overlay.setEnabled(False)
        self._btn_run.setEnabled(False)
        self._progress.setVisible(True)
        bg_white = True
        opacity  = self._opacity_slider.value() / 100.0

        lang = self._lang_combo.currentText() if hasattr(self, "_lang_combo") else "fra"
        self._overlay_worker = OCROverlayWorker(self._engine, self._current_image, lang)
        self._overlay_thread = QThread()
        self._overlay_worker.moveToThread(self._overlay_thread)
        self._overlay_thread.started.connect(self._overlay_worker.run)
        self._overlay_worker.finished.connect(
            lambda lines, w, h: self._on_overlay_done(lines, w, h, bg_white, opacity)
        )
        self._overlay_worker.error.connect(self._on_overlay_error)
        self._overlay_worker.finished.connect(self._overlay_thread.quit)
        self._overlay_worker.error.connect(self._overlay_thread.quit)
        self._overlay_thread.start()

    def _on_overlay_done(self, lines: list, img_w: int, img_h: int, bg_white: bool, opacity: float) -> None:
        self._btn_overlay.setEnabled(True)
        self._btn_run.setEnabled(True)
        self._progress.setVisible(False)
        if not lines:
            QMessageBox.information(self, _("OCR"), _("Aucun texte détecté sur cette page."))
            return
        # 1. Show Qt preview immediately (before writing to PDF)
        self.ocr_lines_ready.emit(lines, img_w, img_h)
        # 2. Write to PDF
        self.overlay_requested.emit(lines, img_w, img_h, bg_white, opacity)

    def _on_preview_setting_changed(self, *_) -> None:
        """Emit preview_settings_changed whenever slider changes."""
        self.preview_settings_changed.emit(self._opacity_slider.value() / 100.0, True)

    def _on_overlay_error(self, msg: str) -> None:
        self._btn_overlay.setEnabled(True)
        self._btn_run.setEnabled(True)
        self._progress.setVisible(False)
        QMessageBox.critical(self, _("Erreur OCR"), msg)

    def _copy_text(self) -> None:
        from PySide6.QtWidgets import QApplication
        QApplication.clipboard().setText(self._text_edit.toPlainText())

    def _export_text(self) -> None:
        path, _fmt = QFileDialog.getSaveFileName(
            self, _("Exporter le texte"), "", _("Fichier texte (*.txt)")
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self._text_edit.toPlainText())
