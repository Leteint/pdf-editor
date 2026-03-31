"""
LRU cache for rendered page images.
Avoids re-rendering pages that haven't changed.
"""
from __future__ import annotations

from collections import OrderedDict
from typing import Optional, Tuple
from PySide6.QtGui import QImage

CacheKey = Tuple[int, float, int]  # (page_index, zoom, rotation)


class PageCache:
    def __init__(self, max_size: int = 30) -> None:
        self._max_size = max_size
        self._cache: OrderedDict[CacheKey, QImage] = OrderedDict()

    def get(self, key: CacheKey) -> Optional[QImage]:
        if key in self._cache:
            self._cache.move_to_end(key)
            return self._cache[key]
        return None

    def put(self, key: CacheKey, image: QImage) -> None:
        if key in self._cache:
            self._cache.move_to_end(key)
        self._cache[key] = image
        if len(self._cache) > self._max_size:
            self._cache.popitem(last=False)

    def invalidate(self, page_index: Optional[int] = None) -> None:
        """Invalidate all entries, or only those for a specific page."""
        if page_index is None:
            self._cache.clear()
        else:
            keys_to_remove = [k for k in self._cache if k[0] == page_index]
            for k in keys_to_remove:
                del self._cache[k]

    def clear(self) -> None:
        self._cache.clear()
