"""
Page organizer dialog — reorder, delete, rotate, and insert pages from
external PDFs or images via drag-and-drop thumbnails.
"""
from __future__ import annotations

from typing import Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QDialogButtonBox, QAbstractItemView, QMessageBox,
    QFileDialog,
)
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt, QSize

from utils.i18n import _


class _PageItem(QListWidgetItem):
    """ListWidgetItem carrying source info, original page index, and rotation."""

    def __init__(
        self,
        source_path: Optional[str],   # None = current doc, str = external PDF
        orig_idx: int,
        pixmap: QPixmap,
        label: str,
    ) -> None:
        super().__init__()
        self.source_path = source_path
        self.orig_idx    = orig_idx
        self.extra_rot   = 0
        self.setIcon(QIcon(pixmap))
        self._base_label = label
        self.setText(label)
        self.setTextAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)
        self.setSizeHint(QSize(130, 165))

    def refresh_label(self) -> None:
        suffix = f" [{self.extra_rot}°]" if self.extra_rot % 360 != 0 else ""
        self.setText(self._base_label + suffix)


class OrganizeDialog(QDialog):
    """
    Shows page thumbnails in a drag-and-drop grid.
    Users can reorder, delete, rotate, and insert pages from other PDFs.

    After exec() == Accepted, read ``page_specs`` to get the ordered list of
    (source_path|None, orig_idx, extra_rot) tuples ready for PDFTools.reorder_pages().
    """

    # Image formats supported for import
    _IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"}

    def __init__(self, renderer, page_count: int, parent=None,
                 initial_files: list | None = None) -> None:
        super().__init__(parent)
        self._renderer    = renderer
        self._page_count  = page_count
        self._temp_files: list[str] = []   # temp PDFs created from images
        self.setWindowTitle(_("Organiser les pages"))
        self.resize(920, 580)
        self._build()
        self._load_original_thumbnails()
        for path in (initial_files or []):
            self._add_file_to_list_from_path(path)

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setSpacing(6)

        info = QLabel(
            _("Glissez les vignettes pour réordonner · "
              "Sélectionnez une ou plusieurs pages puis utilisez les boutons.")
        )
        info.setWordWrap(True)
        root.addWidget(info)

        # ── Thumbnail list ───────────────────────────────────────────────
        self._list = QListWidget()
        self._list.setViewMode(QListWidget.ViewMode.IconMode)
        self._list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self._list.setMovement(QListWidget.Movement.Free)
        self._list.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self._list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self._list.setIconSize(QSize(110, 130))
        self._list.setSpacing(6)
        self._list.setUniformItemSizes(True)
        root.addWidget(self._list, stretch=1)

        # ── Action buttons ───────────────────────────────────────────────
        btn_row = QHBoxLayout()

        self._btn_add   = QPushButton("➕ " + _("Ajouter un document…"))
        self._btn_up    = QPushButton("▲ " + _("Monter"))
        self._btn_down  = QPushButton("▼ " + _("Descendre"))
        self._btn_rotL  = QPushButton("↺ -90°")
        self._btn_rotR  = QPushButton("↻ +90°")
        self._btn_rot180= QPushButton("↕ 180°")
        self._btn_del   = QPushButton("🗑 " + _("Supprimer"))
        self._btn_del.setStyleSheet("color: #e55;")

        for btn in (self._btn_add, self._btn_up, self._btn_down,
                    self._btn_rotL, self._btn_rotR, self._btn_rot180,
                    self._btn_del):
            btn_row.addWidget(btn)
        btn_row.addStretch()

        self._btn_add.clicked.connect(self._add_document)
        self._btn_up.clicked.connect(self._move_up)
        self._btn_down.clicked.connect(self._move_down)
        self._btn_rotL.clicked.connect(lambda: self._rotate_selected(-90))
        self._btn_rotR.clicked.connect(lambda: self._rotate_selected(90))
        self._btn_rot180.clicked.connect(lambda: self._rotate_selected(180))
        self._btn_del.clicked.connect(self._delete_selected)

        root.addLayout(btn_row)

        # ── Counter ──────────────────────────────────────────────────────
        self._counter = QLabel()
        self._list.model().rowsInserted.connect(self._update_counter)
        self._list.model().rowsRemoved.connect(self._update_counter)
        root.addWidget(self._counter)

        # ── Dialog buttons ───────────────────────────────────────────────
        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        btns.button(QDialogButtonBox.StandardButton.Ok).setText(_("Appliquer"))
        btns.accepted.connect(self._validate)
        btns.rejected.connect(self.reject)
        root.addWidget(btns)

    # ------------------------------------------------------------------
    # Thumbnails
    # ------------------------------------------------------------------

    def _load_original_thumbnails(self) -> None:
        self._list.clear()
        for i in range(self._page_count):
            pixmap = self._render_thumb_from_renderer(i)
            item = _PageItem(None, i, pixmap, f"p. {i + 1}")
            self._list.addItem(item)
        self._update_counter()

    def _render_thumb_from_renderer(self, page_idx: int, rot: int = 0) -> QPixmap:
        if self._renderer is None:
            return self._grey_thumb()
        try:
            qimg = self._renderer.render_page(page_idx, zoom=0.18, rotation=rot % 360)
            if qimg:
                return QPixmap.fromImage(qimg)
        except Exception:
            pass
        return self._grey_thumb()

    def _render_thumb_from_path(self, pdf_path: str, page_idx: int) -> QPixmap:
        try:
            import pypdfium2 as pdfium
            doc  = pdfium.PdfDocument(pdf_path)
            page = doc[page_idx]
            bm   = page.render(scale=0.18 * 96 / 72)
            pil  = bm.to_pil().convert("RGBA")
            page.close()
            doc.close()
            from PySide6.QtGui import QImage
            data  = pil.tobytes("raw", "RGBA")
            qimg  = QImage(data, pil.width, pil.height,
                           pil.width * 4, QImage.Format.Format_RGBA8888)
            qimg._data = data
            return QPixmap.fromImage(qimg)
        except Exception:
            return self._grey_thumb()

    @staticmethod
    def _grey_thumb() -> QPixmap:
        pm = QPixmap(110, 130)
        pm.fill(Qt.GlobalColor.darkGray)
        return pm

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _add_file_to_list_from_path(self, path: str) -> None:
        """Add all pages of a PDF or image file to the page list."""
        try:
            import os, pikepdf
            ext = os.path.splitext(path)[1].lower()
            if ext in self._IMAGE_EXTS:
                pdf_path = self._image_to_temp_pdf(path)
                self._temp_files.append(pdf_path)
            else:
                pdf_path = path
            with pikepdf.open(pdf_path) as doc:
                n = len(doc.pages)
            short = os.path.basename(path)
            for i in range(n):
                pixmap = self._render_thumb_from_path(pdf_path, i)
                label  = f"{short}\np. {i + 1}" if n > 1 else short
                item   = _PageItem(pdf_path, i, pixmap, label)
                self._list.addItem(item)
        except Exception as e:
            QMessageBox.critical(self, _("Erreur"), str(e))

    def _add_document(self) -> None:
        filt = (
            _("Documents supportés") +
            " (*.pdf *.jpg *.jpeg *.png *.bmp *.tiff *.tif *.webp);;"
            "PDF (*.pdf);;"
            + _("Images") +
            " (*.jpg *.jpeg *.png *.bmp *.tiff *.tif *.webp)"
        )
        path, _filt = QFileDialog.getOpenFileName(
            self, _("Ajouter un document"), "", filt
        )
        if not path:
            return
        self._add_file_to_list_from_path(path)

    @staticmethod
    def _image_to_temp_pdf(image_path: str) -> str:
        """Convert any supported image to a temporary PDF file.
        Returns the temp file path (caller is responsible for cleanup)."""
        import tempfile, os

        # Try img2pdf first — lossless for JPEG, correct for PNG/TIFF multi-page
        try:
            import img2pdf
            pdf_bytes = img2pdf.convert(image_path)
        except Exception:
            # Fallback: Pillow (handles WebP, BMP, unusual formats)
            from PIL import Image
            import io
            bio = io.BytesIO()
            with Image.open(image_path) as img:
                frames: list = []
                try:
                    while True:
                        frames.append(img.copy().convert("RGB"))
                        img.seek(img.tell() + 1)
                except EOFError:
                    pass
                if not frames:
                    frames = [img.convert("RGB")]
                if len(frames) == 1:
                    frames[0].save(bio, format="PDF")
                else:
                    frames[0].save(bio, format="PDF",
                                   save_all=True, append_images=frames[1:])
            pdf_bytes = bio.getvalue()

        tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        tmp.write(pdf_bytes)
        tmp.close()
        return tmp.name

    def closeEvent(self, event) -> None:  # noqa: N802
        """Clean up temporary PDF files created from images."""
        import os
        for p in self._temp_files:
            try:
                os.unlink(p)
            except Exception:
                pass
        super().closeEvent(event)

    def _selected_rows(self) -> list[int]:
        return sorted(self._list.row(it) for it in self._list.selectedItems())

    def _move_up(self) -> None:
        rows = self._selected_rows()
        if not rows or rows[0] == 0:
            return
        for row in rows:
            item = self._list.takeItem(row)
            self._list.insertItem(row - 1, item)
        self._list.clearSelection()
        for row in rows:
            self._list.item(row - 1).setSelected(True)

    def _move_down(self) -> None:
        rows = self._selected_rows()
        if not rows or rows[-1] >= self._list.count() - 1:
            return
        for row in reversed(rows):
            item = self._list.takeItem(row)
            self._list.insertItem(row + 1, item)
        self._list.clearSelection()
        for row in rows:
            self._list.item(row + 1).setSelected(True)

    def _rotate_selected(self, degrees: int) -> None:
        for item in self._list.selectedItems():
            assert isinstance(item, _PageItem)
            item.extra_rot = (item.extra_rot + degrees) % 360
            # Re-render thumbnail with new rotation
            if item.source_path is None:
                pixmap = self._render_thumb_from_renderer(item.orig_idx, item.extra_rot)
            else:
                pixmap = self._render_thumb_from_path(item.source_path, item.orig_idx)
                # rotate pixmap in Qt if needed
                if item.extra_rot:
                    from PySide6.QtGui import QTransform
                    pixmap = pixmap.transformed(QTransform().rotate(item.extra_rot))
                    pixmap = pixmap.scaled(110, 130,
                                          Qt.AspectRatioMode.KeepAspectRatio,
                                          Qt.TransformationMode.SmoothTransformation)
            item.setIcon(QIcon(pixmap))
            item.refresh_label()

    def _delete_selected(self) -> None:
        for item in self._list.selectedItems():
            self._list.takeItem(self._list.row(item))

    def _update_counter(self, *_args) -> None:
        n = self._list.count()
        self._counter.setText(
            _("{n} page(s) au total — {orig} d'origine, {removed} supprimée(s)").format(
                n=n,
                orig=sum(1 for i in range(n)
                         if isinstance(self._list.item(i), _PageItem)
                         and self._list.item(i).source_path is None),   # type: ignore
                removed=self._page_count - sum(
                    1 for i in range(n)
                    if isinstance(self._list.item(i), _PageItem)
                    and self._list.item(i).source_path is None),        # type: ignore
            )
        )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def _validate(self) -> None:
        if self._list.count() == 0:
            QMessageBox.warning(self, _("Attention"),
                                _("Le document ne peut pas être vide."))
            return
        self.accept()

    # ------------------------------------------------------------------
    # Result
    # ------------------------------------------------------------------

    @property
    def page_specs(self) -> list[tuple]:
        """Ordered list of (source_path|None, orig_idx, extra_rot)."""
        result = []
        for i in range(self._list.count()):
            item = self._list.item(i)
            assert isinstance(item, _PageItem)
            result.append((item.source_path, item.orig_idx, item.extra_rot))
        return result
