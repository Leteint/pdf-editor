"""
Page renderer — converts PDF pages to QImage via pdfium2.
"""
from __future__ import annotations

from typing import Optional
import pypdfium2 as pdfium
from PySide6.QtGui import QImage


class Renderer:
    """
    Opens a PDF with pdfium2 (independently from pikepdf) for rendering.
    Kept separate so the render engine can be swapped without touching core logic.
    """

    def __init__(self) -> None:
        self._doc: Optional[pdfium.PdfDocument] = None
        self._path: Optional[str] = None

    def load(self, path: str, password: str = "") -> None:
        self.close()
        self._doc = pdfium.PdfDocument(path, password=password or None)
        self._path = path

    def load_from_bytes(self, data: bytes) -> None:
        """Reload renderer from in-memory PDF bytes (after in-place edit)."""
        self.close()
        self._bytes_ref = data  # keep alive — pdfium may reference the buffer
        self._doc = pdfium.PdfDocument(data)
        # _path stays unchanged — it refers to the on-disk source

    def close(self) -> None:
        if self._doc:
            self._doc.close()
            self._doc = None

    def render_page(self, index: int, zoom: float = 1.0, rotation: int = 0) -> Optional[QImage]:
        """
        Render page at given zoom level.
        Returns a QImage (RGBA8888) or None on error.
        """
        if not self._doc:
            return None

        page = self._doc[index]
        scale = zoom * (96 / 72)  # 96 DPI target
        bitmap = page.render(scale=scale, rotation=rotation)
        pil_image = bitmap.to_pil()

        # Convert PIL → QImage
        pil_image = pil_image.convert("RGBA")
        data = pil_image.tobytes("raw", "RGBA")
        qimage = QImage(
            data,
            pil_image.width,
            pil_image.height,
            pil_image.width * 4,
            QImage.Format.Format_RGBA8888,
        )
        # Keep data alive
        qimage._data = data
        page.close()
        return qimage

    def get_page_size(self, index: int, zoom: float = 1.0) -> tuple[float, float]:
        """Return (width, height) in pixels at given zoom."""
        if not self._doc:
            return (0, 0)
        page = self._doc[index]
        w, h = page.get_size()
        scale = zoom * (96 / 72)
        page.close()
        return (w * scale, h * scale)

    @property
    def page_count(self) -> int:
        return len(self._doc) if self._doc else 0

    @property
    def is_open(self) -> bool:
        return self._doc is not None
