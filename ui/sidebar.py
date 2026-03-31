"""
Sidebar with thumbnail list and bookmarks.
"""
from __future__ import annotations

from typing import Optional
from PySide6.QtCore import Qt, Signal, QSize, QThread, QObject
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QListWidgetItem,
    QLabel, QTabWidget, QSizePolicy,
)

from core.renderer import Renderer


class ThumbnailLoader(QObject):
    """Renders thumbnails in background."""
    thumbnail_ready = Signal(int, QImage)

    def __init__(self, renderer: Renderer) -> None:
        super().__init__()
        self._renderer = renderer
        self._cancelled = False

    def run(self, page_count: int) -> None:
        self._cancelled = False
        for i in range(page_count):
            if self._cancelled:
                break
            img = self._renderer.render_page(i, zoom=0.15)
            if img:
                self.thumbnail_ready.emit(i, img)

    def cancel(self) -> None:
        self._cancelled = True


class ThumbnailPanel(QWidget):
    page_selected = Signal(int)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)

        self._list = QListWidget()
        self._list.setIconSize(QSize(120, 160))
        self._list.setSpacing(4)
        self._list.currentRowChanged.connect(self.page_selected.emit)
        layout.addWidget(self._list)

    def clear(self) -> None:
        self._list.clear()

    def add_placeholder(self, index: int) -> None:
        item = QListWidgetItem(f"Page {index + 1}")
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self._list.addItem(item)

    def set_thumbnail(self, index: int, image: QImage) -> None:
        if index < self._list.count():
            pixmap = QPixmap.fromImage(image)
            item = self._list.item(index)
            item.setIcon(pixmap)

    def select_page(self, index: int) -> None:
        self._list.blockSignals(True)
        self._list.setCurrentRow(index)
        self._list.blockSignals(False)


class Sidebar(QWidget):
    page_selected = Signal(int)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setMinimumWidth(150)
        self.setMaximumWidth(250)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._tabs = QTabWidget()
        self._thumb_panel = ThumbnailPanel()
        self._thumb_panel.page_selected.connect(self.page_selected.emit)

        self._tabs.addTab(self._thumb_panel, "Pages")
        layout.addWidget(self._tabs)

    def load_thumbnails(self, renderer: Renderer) -> None:
        self._thumb_panel.clear()
        count = renderer.page_count
        for i in range(count):
            self._thumb_panel.add_placeholder(i)
        # Render thumbnails lazily
        for i in range(min(count, 50)):  # limit for large docs
            img = renderer.render_page(i, zoom=0.15)
            if img:
                self._thumb_panel.set_thumbnail(i, img)

    def select_page(self, index: int) -> None:
        self._thumb_panel.select_page(index)

    def clear(self) -> None:
        self._thumb_panel.clear()
