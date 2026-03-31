"""
Dialogue de création d'un champ de formulaire.
"""
from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QComboBox,
    QDialogButtonBox, QVBoxLayout, QLabel, QTextEdit,
    QHBoxLayout, QWidget, QPushButton, QFileDialog, QSpinBox,
    QDoubleSpinBox, QToolButton, QColorDialog, QCheckBox,
)
from PySide6.QtGui import QColor, QIcon
from PySide6.QtCore import Qt
from utils.i18n import _

_TYPES = [
    ("texte",    "Bloc de texte"),
    ("text",     "Input texte"),
    ("checkbox", "Case à cocher"),
    ("radio",    "Boutons radio"),
    ("dropdown", "Liste déroulante"),
    ("image",    "Image"),
]


class _ColorButton(QPushButton):
    """Small button that shows a color swatch and opens a color picker."""
    def __init__(self, color: str = "#000000", parent=None) -> None:
        super().__init__(parent)
        self._color = color
        self.setFixedSize(32, 28)
        self._refresh()
        self.clicked.connect(self._pick)

    def _refresh(self) -> None:
        self.setStyleSheet(
            f"QPushButton {{ background:{self._color}; border:1px solid #888; border-radius:3px; }}"
        )

    def _pick(self) -> None:
        c = QColorDialog.getColor(QColor(self._color), self, _("Couleur du texte"))
        if c.isValid():
            self._color = c.name()
            self._refresh()

    @property
    def color(self) -> str:
        return self._color


class AddFieldDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(_("Ajouter un champ"))
        self.setMinimumWidth(400)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self._name_edit = QLineEdit()
        self._name_edit.setPlaceholderText("ex: nom, actif, genre…")
        self._name_label = QLabel(_("Nom du champ :"))
        form.addRow(self._name_label, self._name_edit)

        self._type_combo = QComboBox()
        for _ftype, label in _TYPES:
            self._type_combo.addItem(label)
        self._type_combo.currentIndexChanged.connect(self._on_type_changed)
        form.addRow(_("Type :"), self._type_combo)

        # Options row (radio/dropdown/label) + browse button (image)
        self._options_label = QLabel(_("Options (séparées par ; ) :"))
        options_row = QWidget()
        options_row_layout = QHBoxLayout(options_row)
        options_row_layout.setContentsMargins(0, 0, 0, 0)
        self._options_edit = QLineEdit()
        self._options_edit.setPlaceholderText("ex: Homme;Femme;Autre")
        self._browse_btn = QPushButton(_("Parcourir…"))
        self._browse_btn.setVisible(False)
        self._browse_btn.clicked.connect(self._browse_image)
        options_row_layout.addWidget(self._options_edit)
        options_row_layout.addWidget(self._browse_btn)
        form.addRow(self._options_label, options_row)

        # Multi-line content for "texte" type
        self._content_label = QLabel(_("Contenu :"))
        self._content_text = QTextEdit()
        self._content_text.setMaximumHeight(90)
        self._content_text.setPlaceholderText(_("Entrez votre texte ici…"))
        self._content_label.setVisible(False)
        self._content_text.setVisible(False)
        form.addRow(self._content_label, self._content_text)

        # ── Formatting row (label + texte only) ──────────────────────────
        self._fmt_label = QLabel(_("Mise en forme :"))
        fmt_row = QWidget()
        fmt_layout = QHBoxLayout(fmt_row)
        fmt_layout.setContentsMargins(0, 0, 0, 0)
        fmt_layout.setSpacing(4)

        # Font size
        fmt_layout.addWidget(QLabel(_("Taille :")))
        self._font_size_spin = QSpinBox()
        self._font_size_spin.setRange(6, 144)
        self._font_size_spin.setValue(12)
        self._font_size_spin.setSuffix(" pt")
        self._font_size_spin.setFixedWidth(70)
        fmt_layout.addWidget(self._font_size_spin)

        fmt_layout.addSpacing(6)

        # Bold
        self._btn_bold = QToolButton()
        self._btn_bold.setText("B")
        self._btn_bold.setCheckable(True)
        self._btn_bold.setFixedSize(28, 28)
        self._btn_bold.setStyleSheet(
            "QToolButton { font-weight:bold; }"
            "QToolButton:checked { background:#f9a825; border-radius:3px; }"
        )
        fmt_layout.addWidget(self._btn_bold)

        # Italic
        self._btn_italic = QToolButton()
        self._btn_italic.setText("I")
        self._btn_italic.setCheckable(True)
        self._btn_italic.setFixedSize(28, 28)
        self._btn_italic.setStyleSheet(
            "QToolButton { font-style:italic; }"
            "QToolButton:checked { background:#f9a825; border-radius:3px; }"
        )
        fmt_layout.addWidget(self._btn_italic)

        # Underline
        self._btn_underline = QToolButton()
        self._btn_underline.setText("U")
        self._btn_underline.setCheckable(True)
        self._btn_underline.setFixedSize(28, 28)
        self._btn_underline.setStyleSheet(
            "QToolButton { text-decoration:underline; }"
            "QToolButton:checked { background:#f9a825; border-radius:3px; }"
        )
        fmt_layout.addWidget(self._btn_underline)

        fmt_layout.addSpacing(6)

        # Color
        fmt_layout.addWidget(QLabel(_("Couleur :")))
        self._color_btn = _ColorButton("#000000")
        fmt_layout.addWidget(self._color_btn)

        fmt_layout.addSpacing(6)

        # Letter spacing
        fmt_layout.addWidget(QLabel(_("Espac. :")))
        self._spacing_spin = QDoubleSpinBox()
        self._spacing_spin.setRange(0.0, 20.0)
        self._spacing_spin.setSingleStep(0.5)
        self._spacing_spin.setValue(0.0)
        self._spacing_spin.setSuffix(" pt")
        self._spacing_spin.setFixedWidth(70)
        fmt_layout.addWidget(self._spacing_spin)

        fmt_layout.addStretch()

        self._fmt_label.setVisible(False)
        fmt_row.setVisible(False)
        self._fmt_row_widget = fmt_row
        form.addRow(self._fmt_label, fmt_row)

        # ── Masquer le texte sous-jacent (texte type only) ───────────────
        self._chk_cover = QCheckBox(_("Fond blanc — masquer le texte original en dessous"))
        self._chk_cover.setChecked(True)
        self._chk_cover.setVisible(False)
        form.addRow("", self._chk_cover)

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self._on_type_changed(0)

    # ------------------------------------------------------------------

    def _on_type_changed(self, idx: int) -> None:
        ftype = _TYPES[idx][0]
        show_fmt = ftype == "texte"
        self._fmt_label.setVisible(show_fmt)
        self._fmt_row_widget.setVisible(show_fmt)

        self._chk_cover.setVisible(ftype == "texte")
        if ftype == "texte":
            self._name_label.setText(_("Identifiant :"))
            self._name_edit.setPlaceholderText("ex: intro, instructions")
            self._options_label.setVisible(False)
            self._options_edit.setVisible(False)
            self._browse_btn.setVisible(False)
            self._content_label.setVisible(True)
            self._content_text.setVisible(True)
        elif ftype == "image":
            self._name_label.setText(_("Identifiant :"))
            self._name_edit.setPlaceholderText("ex: logo, photo")
            self._options_label.setText(_("Fichier image :"))
            self._options_edit.setPlaceholderText("ex: C:/images/logo.png")
            self._options_label.setVisible(True)
            self._options_edit.setVisible(True)
            self._browse_btn.setVisible(True)
            self._content_label.setVisible(False)
            self._content_text.setVisible(False)
        elif ftype in ("checkbox", "radio", "dropdown"):
            self._name_label.setText(_("Nom du champ :"))
            self._name_edit.setPlaceholderText("ex: nom, actif, genre…")
            self._options_label.setText(_("Options (séparées par ; ) :"))
            self._options_edit.setPlaceholderText("ex: Homme;Femme;Autre")
            self._options_label.setVisible(True)
            self._options_edit.setVisible(True)
            self._browse_btn.setVisible(False)
            self._content_label.setVisible(False)
            self._content_text.setVisible(False)
        else:
            self._name_label.setText(_("Nom du champ :"))
            self._name_edit.setPlaceholderText("ex: nom, actif, genre…")
            self._options_label.setVisible(False)
            self._options_edit.setVisible(False)
            self._browse_btn.setVisible(False)
            self._content_label.setVisible(False)
            self._content_text.setVisible(False)

        # Resize dialog to fit new content
        self.adjustSize()

    def _browse_image(self) -> None:
        path, _filt = QFileDialog.getOpenFileName(
            self,
            _("Choisir une image"),
            "",
            _("Images (*.png *.jpg *.jpeg *.bmp *.tiff *.gif)"),
        )
        if path:
            self._options_edit.setText(path)

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------

    def field_name(self) -> str:
        return self._name_edit.text().strip()

    def field_type(self) -> str:
        return _TYPES[self._type_combo.currentIndex()][0]

    def field_font_size(self) -> float:
        return float(self._font_size_spin.value())

    def field_bold(self) -> bool:
        return self._btn_bold.isChecked()

    def field_italic(self) -> bool:
        return self._btn_italic.isChecked()

    def field_underline(self) -> bool:
        return self._btn_underline.isChecked()

    def field_color(self) -> str:
        return self._color_btn.color

    def field_letter_spacing(self) -> float:
        return self._spacing_spin.value()

    def field_bg_white(self) -> bool:
        return self._chk_cover.isChecked()

    def field_options(self) -> list[str]:
        ftype = _TYPES[self._type_combo.currentIndex()][0]
        if ftype == "texte":
            raw = self._content_text.toPlainText()
            return [raw.strip()] if raw.strip() else []
        elif ftype == "image":
            raw = self._options_edit.text()
            return [raw.strip()] if raw.strip() else []
        else:
            return [o.strip() for o in self._options_edit.text().split(";") if o.strip()]
