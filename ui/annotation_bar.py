"""
Annotation color picker and properties panel.
"""
from __future__ import annotations

from typing import Optional
from PySide6.QtCore import Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QWidget, QToolBar, QHBoxLayout, QLabel, QPushButton,
    QColorDialog, QDoubleSpinBox, QFrame,
)


class ColorButton(QPushButton):
    color_changed = Signal(str)  # hex color

    def __init__(self, color: str = "#FFFF00", parent=None) -> None:
        super().__init__(parent)
        self._color = color
        self.setFixedSize(28, 24)
        self._update_style()
        self.clicked.connect(self._pick_color)

    def _pick_color(self) -> None:
        color = QColorDialog.getColor(QColor(self._color), self)
        if color.isValid():
            self._color = color.name()
            self._update_style()
            self.color_changed.emit(self._color)

    def _update_style(self) -> None:
        self.setStyleSheet(
            f"background-color: {self._color}; border: 1px solid #888; border-radius: 3px;"
        )

    @property
    def color(self) -> str:
        return self._color

    def set_color(self, color: str) -> None:
        self._color = color
        self._update_style()


class AnnotationPropertiesBar(QToolBar):
    color_changed = Signal(str)
    stroke_width_changed = Signal(float)

    # Preset colors
    PRESETS = [
        ("#FFFF00", "Jaune"),
        ("#FF6B6B", "Rouge"),
        ("#6BFF6B", "Vert"),
        ("#6BB5FF", "Bleu"),
        ("#FF9900", "Orange"),
        ("#CC66FF", "Violet"),
    ]

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__("Propriétés annotation", parent)
        self.setMovable(False)
        self._current_color = "#FFFF00"
        self._build_ui()

    def _build_ui(self) -> None:
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(4)

        layout.addWidget(QLabel("Couleur :"))

        for hex_color, name in self.PRESETS:
            btn = QPushButton()
            btn.setFixedSize(20, 20)
            btn.setToolTip(name)
            btn.setStyleSheet(
                f"background-color:{hex_color}; border:1px solid #555; border-radius:2px;"
            )
            btn.clicked.connect(lambda checked, c=hex_color: self._select_color(c))
            layout.addWidget(btn)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        layout.addWidget(sep)

        self._custom_btn = ColorButton(self._current_color)
        self._custom_btn.color_changed.connect(self._select_color)
        layout.addWidget(self._custom_btn)
        layout.addWidget(QLabel("Personnalisé"))

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.VLine)
        layout.addWidget(sep2)

        layout.addWidget(QLabel("Épaisseur :"))
        self._width_spin = QDoubleSpinBox()
        self._width_spin.setRange(0.5, 10.0)
        self._width_spin.setValue(2.0)
        self._width_spin.setSingleStep(0.5)
        self._width_spin.setFixedWidth(60)
        self._width_spin.valueChanged.connect(self.stroke_width_changed.emit)
        layout.addWidget(self._width_spin)

        layout.addStretch()
        self.addWidget(container)

    def _select_color(self, color: str) -> None:
        self._current_color = color
        self._custom_btn.set_color(color)
        self.color_changed.emit(color)

    @property
    def current_color(self) -> str:
        return self._current_color

    @property
    def current_stroke_width(self) -> float:
        return self._width_spin.value()
