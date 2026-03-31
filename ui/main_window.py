"""
Main application window.
Connects all components: Document, Renderer, Viewer, Sidebar, Toolbars, Panels.
"""
from __future__ import annotations

import os


from typing import Optional
from utils.i18n import _, SUPPORTED_LANGUAGES, get_language

from PySide6.QtCore import Qt, QRectF, Signal
from PySide6.QtGui import QAction, QKeySequence, QCloseEvent, QPixmap
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QSplitter,
    QFileDialog, QMessageBox, QStatusBar, QDockWidget,
    QInputDialog, QApplication, QLineEdit, QVBoxLayout,
)

from core.document import Document
from core.renderer import Renderer
from core.annotations import AnnotationManager, Annotation
from core.ocr import OCREngine
from utils.cache import PageCache
from utils.config import Config
from utils.history import History, Command

from ui.viewer import PDFViewer
from ui.sidebar import Sidebar
from ui.toolbar import MainToolBar, PagesToolBar
from ui.panels.search import SearchPanel
from ui.panels.ocr_panel import OCRPanel
from ui.panels.form_panel import FormPanel
from ui.panels.tool_panel import LeftToolPanel
from ui.panels.language_panel import LanguagePanel
from ui.panels.help_panel import HelpPanel
from ui.dialogs.add_field_dialog import AddFieldDialog
from core.forms import FormManager

# Ratio of box height to font size for OCR-injected labels (line height ≈ 1.35 em).
_LINE_HEIGHT_RATIO = 1.35

# ---------------------------------------------------------------------------
# Undoable commands
# ---------------------------------------------------------------------------

class AnnotationAddCommand(Command):
    def __init__(self, manager: AnnotationManager, ann: Annotation, viewer: PDFViewer) -> None:
        self._manager = manager
        self._ann = ann
        self._viewer = viewer

    def execute(self) -> None:
        self._manager.add(self._ann)
        d = self._ann.to_dict()
        if hasattr(self._ann, "_extra_fmt"):
            d.update(self._ann._extra_fmt)
        self._viewer.add_annotation(d)

    def undo(self) -> None:
        self._manager.remove(self._ann.id)
        # Rebuild the annotation overlay so the removed annotation disappears
        page = self._viewer.current_page
        self._viewer._page_widget.clear_annotations()
        for ann in self._manager.get_page_annotations(page):
            d = ann.to_dict()
            if hasattr(ann, "_extra_fmt"):
                d.update(ann._extra_fmt)
            self._viewer.add_annotation(d)

    @property
    def description(self) -> str:
        return f"Annoter ({self._ann.type})"


class MoveTextBlockCommand(Command):
    """Undoable move of a text block in the PDF content stream."""

    def __init__(self, pdf, page_index: int, block, new_norm_x: float, new_norm_y: float,
                 reload_fn, cache, viewer) -> None:
        from core.block_detector import _read_stream_bytes
        self._pdf = pdf
        self._page_index = page_index
        self._block = block
        self._new_norm_x = new_norm_x
        self._new_norm_y = new_norm_y
        self._reload_fn = reload_fn
        self._cache = cache
        self._viewer = viewer

        # Save original bytes of every stream touched by this block
        page = pdf.pages[page_index]
        contents = page.get("/Contents")
        import pikepdf as _pikepdf
        streams = list(contents) if isinstance(contents, _pikepdf.Array) else [contents]
        affected = {item.stream_index for line in block.lines for item in line.items}
        self._saved: dict[int, bytes] = {}
        for si in affected:
            if si < len(streams):
                raw = _read_stream_bytes(streams[si])
                if raw is not None:
                    self._saved[si] = raw

    def execute(self) -> None:
        from core.text_mover import move_text_block
        move_text_block(self._pdf, self._page_index, self._block,
                        self._new_norm_x, self._new_norm_y)
        self._reload_fn()
        self._cache.invalidate(self._page_index)
        self._viewer.refresh()

    def undo(self) -> None:
        from core.text_editor import stream_write_compressed
        import pikepdf as _pikepdf
        page = self._pdf.pages[self._page_index]
        contents = page.get("/Contents")
        streams = list(contents) if isinstance(contents, _pikepdf.Array) else [contents]
        for si, raw in self._saved.items():
            if si < len(streams):
                stream_write_compressed(streams[si], raw)
        self._reload_fn()
        self._cache.invalidate(self._page_index)
        self._viewer.refresh()

    @property
    def description(self) -> str:
        text = self._block.text[:30].replace("\n", " ")
        return f"Déplacer « {text} »"


class PageRotateCommand(Command):
    def __init__(self, document: Document, renderer: Renderer, viewer: PDFViewer,
                 page: int, degrees: int, cache: PageCache,
                 reload_fn=None) -> None:
        self._doc = document
        self._renderer = renderer
        self._viewer = viewer
        self._page = page
        self._degrees = degrees
        self._cache = cache
        self._reload_fn = reload_fn  # callable: saves pikepdf→tmp, reloads renderer

    def execute(self) -> None:
        self._doc.rotate_page(self._page, self._degrees)
        if self._reload_fn:
            self._reload_fn()
        self._cache.invalidate(self._page)
        self._viewer.refresh()

    def undo(self) -> None:
        self._doc.rotate_page(self._page, -self._degrees)
        if self._reload_fn:
            self._reload_fn()
        self._cache.invalidate(self._page)
        self._viewer.refresh()

    @property
    def description(self) -> str:
        return f"Rotation page {self._page + 1} ({self._degrees}°)"


# ---------------------------------------------------------------------------
# Helpers for PDF-level snapshot commands
# ---------------------------------------------------------------------------

def _snapshot_page_streams(pdf) -> list:
    """Capture raw bytes of every page's content stream(s)."""
    import pikepdf as _pk
    result = []
    for page in pdf.pages:
        pg = page.obj
        c = pg.get("/Contents")
        if c is None:
            result.append(("none", None))
        elif isinstance(c, _pk.Array):
            result.append(("array", [bytes(s.read_raw_bytes()) for s in c]))
        else:
            result.append(("single", bytes(c.read_raw_bytes())))
    return result


def _restore_page_streams(pdf, snapshot: list) -> None:
    """Restore page content streams from a snapshot."""
    import pikepdf as _pk
    for page, (kind, data) in zip(pdf.pages, snapshot):
        pg = page.obj
        if kind == "none":
            if "/Contents" in pg:
                del pg["/Contents"]
        elif kind == "array":
            streams = [pdf.make_indirect(_pk.Stream(pdf, d)) for d in data]
            pg["/Contents"] = _pk.Array(streams)
        else:
            pg["/Contents"] = pdf.make_indirect(_pk.Stream(pdf, data))


def _snapshot_pdf_bytes(pdf) -> bytes:
    """Serialize the full PDF to bytes (for structural changes)."""
    from io import BytesIO
    buf = BytesIO()
    pdf.save(buf)
    return buf.getvalue()


def _restore_pdf_from_bytes(pdf, data: bytes) -> None:
    """Replace all pages of *pdf* in-place from serialized bytes."""
    import pikepdf as _pk
    from io import BytesIO
    src = _pk.Pdf.open(BytesIO(data))
    # Replace pages using copy_foreign so src can be closed safely
    del pdf.pages[:]
    for i in range(len(src.pages)):
        pdf.pages.append(_pk.Page(pdf.copy_foreign(src.pages[i].obj)))
    # Restore docinfo
    for key in list(pdf.docinfo.keys()):
        try:
            del pdf.docinfo[key]
        except Exception:
            pass
    for key, val in src.docinfo.items():
        try:
            pdf.docinfo[key] = val
        except Exception:
            pass
    src.close()


class PageStreamsCommand(Command):
    """Generic command for operations that only modify page content streams
    (watermark, header/footer, stamp, compress).
    execute() is safe to call twice (redo: restores the 'after' snapshot)."""

    def __init__(self, pdf, operation_fn, desc: str, refresh_fn) -> None:
        self._pdf = pdf
        self._op = operation_fn
        self._desc = desc
        self._refresh = refresh_fn
        self._before = _snapshot_page_streams(pdf)
        self._after: list | None = None

    def execute(self) -> None:
        if self._after is None:
            # First call: actually run the operation
            self._op()
            self._after = _snapshot_page_streams(self._pdf)
        else:
            # Redo call: restore the 'after' snapshot
            _restore_page_streams(self._pdf, self._after)
        self._refresh()

    def undo(self) -> None:
        _restore_page_streams(self._pdf, self._before)
        self._refresh()

    @property
    def description(self) -> str:
        return self._desc


class MetadataCommand(Command):
    """Undoable metadata edit."""

    def __init__(self, pdf, old_meta: dict, new_meta: dict, apply_fn, refresh_fn) -> None:
        self._pdf = pdf
        self._old = old_meta
        self._new = new_meta
        self._apply = apply_fn
        self._refresh = refresh_fn

    def execute(self) -> None:
        self._apply(self._new)
        self._refresh()

    def undo(self) -> None:
        self._apply(self._old)
        self._refresh()

    @property
    def description(self) -> str:
        return "Modifier les métadonnées"


class PdfStructureCommand(Command):
    """Generic command for structural changes (reorder, delete page).
    Snapshots the full PDF as bytes before/after."""

    def __init__(self, pdf, operation_fn, desc: str, refresh_fn) -> None:
        self._pdf = pdf
        self._op = operation_fn
        self._desc = desc
        self._refresh = refresh_fn
        self._before = _snapshot_pdf_bytes(pdf)
        self._after: bytes | None = None

    def execute(self) -> None:
        if self._after is None:
            self._op()
            self._after = _snapshot_pdf_bytes(self._pdf)
        else:
            _restore_pdf_from_bytes(self._pdf, self._after)
        self._refresh()

    def undo(self) -> None:
        _restore_pdf_from_bytes(self._pdf, self._before)
        self._refresh()

    @property
    def description(self) -> str:
        return self._desc


# ---------------------------------------------------------------------------
# Main window
# ---------------------------------------------------------------------------

class MainWindow(QMainWindow):
    def __init__(self, config: Config) -> None:
        super().__init__()
        self._config = config
        self._document = Document()
        self._renderer = Renderer()
        self._annotations = AnnotationManager()
        self._cache = PageCache(max_size=30)
        self._history = History()
        self._ocr_engine = OCREngine(config.get("tesseract_path", ""))
        self._current_tool = "select"
        self._current_color = "#FFFF00"
        self._current_stroke = 2.0
        self._last_word_info: dict = {}
        self._last_edit_page: int = 0
        self._editing_label: Optional[dict] = None        # set when double-clicking a form label
        self._editing_freetext_ann: Optional[dict] = None  # set when double-clicking a freetext overlay
        self._edit_tempfile: Optional[str] = None   # temp file for renderer after in-place edits
        self._pending_ocr_lines: list = []           # last OCR run lines (for dynamic preview)
        self._pending_ocr_img_w: int = 1
        self._pending_ocr_img_h: int = 1
        self._ocr_overlay_widths: dict[int, float] = {}  # index → overridden norm_w after resize
        # Chain of (page, old_text, new_text) — lets us resolve the current text for any
        # word even though pdfplumber always reads from the original on-disk file.
        self._edit_chain: list[tuple[int, str, str]] = []
        self._form_design_syncing = False  # prevents recursive signal loop
        self._injected_blocks: dict[str, str] = {}   # block_key → block_id
        self._injected_meta: dict[str, dict] = {}    # block_id → formatting metadata
        self._last_deletable: Optional[dict] = None  # last right-clicked deletable element
        self._debug_move_dock = None   # debug dock widget for block moves

        self._build_ui()
        self._connect_signals()
        self._update_title()
        self._update_actions()

        self.resize(1200, 800)

    # ------------------------------------------------------------------
    # Build UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        self.setWindowTitle("PDF Editor")

        # --- Toolbars ---
        self._main_toolbar = MainToolBar(self)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self._main_toolbar)

        self._pages_toolbar = PagesToolBar(self)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self._pages_toolbar)
        self.addToolBarBreak(Qt.ToolBarArea.TopToolBarArea)

        # --- Central area ---
        self._viewer = PDFViewer(self._renderer, self._cache)
        central = QWidget()
        from PySide6.QtWidgets import QVBoxLayout
        cl = QVBoxLayout(central)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.addWidget(self._viewer)
        self.setCentralWidget(central)

        # --- Left sidebar (thumbnails) ---
        self._sidebar = Sidebar()
        self._sidebar_dock = QDockWidget(_("Pages"), self)
        self._sidebar_dock.setWidget(self._sidebar)
        self._sidebar_dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable |
            QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self._sidebar_dock)

        # --- Left tool panel (accordion) ---
        self._left_tool_panel = LeftToolPanel()
        self._left_tool_dock = QDockWidget(_("Outils"), self)
        self._left_tool_dock.setWidget(self._left_tool_panel)
        self._left_tool_dock.setMinimumWidth(160)
        self._left_tool_dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable |
            QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self._left_tool_dock)
        self.tabifyDockWidget(self._sidebar_dock, self._left_tool_dock)

        # --- Language panel ---
        self._lang_panel = LanguagePanel()
        self._lang_dock = QDockWidget(_("Langue"), self)
        self._lang_dock.setWidget(self._lang_panel)
        self._lang_dock.setMinimumWidth(160)
        self._lang_dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable |
            QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self._lang_dock)
        self.tabifyDockWidget(self._left_tool_dock, self._lang_dock)

        # --- Help panel ---
        self._help_panel = HelpPanel()
        self._help_dock = QDockWidget(_("Aide"), self)
        self._help_dock.setWidget(self._help_panel)
        self._help_dock.setMinimumWidth(160)
        self._help_dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable |
            QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self._help_dock)
        self.tabifyDockWidget(self._lang_dock, self._help_dock)

        self._sidebar_dock.raise_()  # show pages tab by default

        # --- Right panel (form only) ---
        self._form_manager = FormManager()
        self._form_panel = FormPanel()
        self._form_panel.save_requested.connect(self.save_file)

        self._right_dock = QDockWidget(_("Formulaire"), self)
        self._right_dock.setWidget(self._form_panel)
        self._right_dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable |
            QDockWidget.DockWidgetFeature.DockWidgetFloatable |
            QDockWidget.DockWidgetFeature.DockWidgetClosable
        )
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self._right_dock)
        self._right_dock.hide()

        # --- Search dock ---
        self._search_panel = SearchPanel()
        self._search_dock = QDockWidget(_("Recherche"), self)
        self._search_dock.setWidget(self._search_panel)
        self._search_dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable |
            QDockWidget.DockWidgetFeature.DockWidgetFloatable |
            QDockWidget.DockWidgetFeature.DockWidgetClosable
        )
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self._search_dock)
        self._search_dock.hide()

        # --- OCR dock ---
        self._ocr_panel = OCRPanel(self._ocr_engine)
        self._ocr_dock = QDockWidget(_("OCR"), self)
        self._ocr_dock.setWidget(self._ocr_panel)
        self._ocr_dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable |
            QDockWidget.DockWidgetFeature.DockWidgetFloatable |
            QDockWidget.DockWidgetFeature.DockWidgetClosable
        )
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self._ocr_dock)
        self._ocr_dock.hide()

        # --- Menu bar ---
        self._build_menu()

        # --- Status bar ---
        self._status = QStatusBar(self)
        self.setStatusBar(self._status)
        self._status.showMessage(_("Bienvenue dans PDF Editor. Ouvrez un fichier pour commencer."))

    def _build_menu(self) -> None:
        mb = self.menuBar()

        # Fichier
        m_file = mb.addMenu(_("Fichier"))
        self._add_action(m_file, "📂  " + _("Ouvrir…"), self.open_file_dialog, "Ctrl+O")
        m_recent = m_file.addMenu("🕒  " + _("Fichiers récents"))
        self._recent_menu = m_recent
        self._refresh_recent_menu()
        m_file.addSeparator()
        self._add_action(m_file, "📋  " + _("Nouveau formulaire vierge…"), self._new_blank_form, "Ctrl+Shift+N")
        m_file.addSeparator()
        self._add_action(m_file, "💾  " + _("Enregistrer"), self.save_file, "Ctrl+S")
        self._add_action(m_file, "💾  " + _("Enregistrer sous…"), self.save_file_as, "Ctrl+Shift+S")
        m_file.addSeparator()
        self._add_action(m_file, "🖨  " + _("Imprimer…"), self._print_document, "Ctrl+P")
        m_file.addSeparator()
        self._add_action(m_file, "✖  " + _("Fermer"), self.close_document, "Ctrl+W")
        m_file.addSeparator()
        self._add_action(m_file, "🚪  " + _("Quitter"), self.close, "Alt+F4")

        # Édition
        m_edit = mb.addMenu(_("Édition"))
        self._action_undo = self._add_action(m_edit, "↩  " + _("Annuler"), self.undo, "Ctrl+Z")
        self._action_redo = self._add_action(m_edit, "↪  " + _("Rétablir"), self.redo, "Ctrl+Y")
        m_edit.addSeparator()
        self._add_action(m_edit, "🔍  " + _("Rechercher…"), self._open_search, "Ctrl+F")

        # Affichage
        m_view = mb.addMenu(_("Affichage"))
        self._add_action(m_view, "🔎  " + _("Zoom +"), self._viewer.zoom_in, "Ctrl+=")
        self._add_action(m_view, "🔍  " + _("Zoom -"), self._viewer.zoom_out, "Ctrl+-")
        self._add_action(m_view, "⬜  " + _("Ajuster à la page"), self._viewer.zoom_fit_page, "Ctrl+0")
        self._add_action(m_view, "↔  " + _("Ajuster à la largeur"), self._viewer.zoom_fit_width, "Ctrl+1")
        m_view.addSeparator()
        self._add_action(m_view, "◧  " + _("Afficher/masquer le panneau Pages"),
                         self._toggle_sidebar, "F4")
        self._add_action(m_view, "🔧  " + _("Afficher/masquer les outils"),
                         self._toggle_right_panel, "F5")
        m_view.addSeparator()
        self._add_action(m_view, "🌙  " + _("Thème sombre"), lambda: self._switch_theme("dark"))
        self._add_action(m_view, "☀  " + _("Thème clair"), lambda: self._switch_theme("light"))

        # Langue
        m_lang = mb.addMenu(_("Langue"))
        current_lang = get_language()
        for code, display_name in SUPPORTED_LANGUAGES.items():
            flag = {"fr": "🇫🇷", "en": "🇬🇧", "de": "🇩🇪", "es": "🇪🇸",
                    "it": "🇮🇹", "pt": "🇵🇹", "ru": "🇷🇺"}.get(code, "")
            a = QAction(f"{flag}  {display_name}", self)
            a.setCheckable(True)
            a.setChecked(code == current_lang)
            a.triggered.connect(lambda checked, c=code: self._change_language(c))
            m_lang.addAction(a)

        # Outils
        m_tools = mb.addMenu(_("Outils"))
        self._add_action(m_tools, "🖼  " + _("Insérer une image…"), self._insert_image_from_menu)
        self._add_action(m_tools, "📝  " + _("Insérer un bloc de texte…"), lambda: self._on_form_design_mode(True))
        self._add_action(m_tools, "↔  " + _("Déplacer un bloc de texte"), self._activate_move_block_tool, "M")
        m_tools.addSeparator()
        self._add_action(m_tools, "⊕  " + _("Réorganiser/Fusionner les pages…"), self._organize_pages)
        self._add_action(m_tools, "✂  " + _("Fractionner ce PDF…"), self._split_pdf)
        self._add_action(m_tools, "🗑  " + _("Supprimer la page courante"), self._delete_current_page, "Ctrl+Delete")
        m_tools.addSeparator()
        self._add_action(m_tools, "📄  " + _("Extraire le texte…"), self._extract_text)
        self._add_action(m_tools, "🖼  " + _("Extraire les images…"), self._extract_images)
        m_tools.addSeparator()
        self._add_action(m_tools, "ℹ  " + _("Métadonnées…"), self._edit_metadata)
        self._add_action(m_tools, "☰  " + _("En-têtes et pieds de page…"), self._add_header_footer)
        self._add_action(m_tools, "◈  " + _("Filigrane…"), self._add_watermark)
        self._add_action(m_tools, "🖊  " + _("Tampon texte…"), self._add_stamp)
        self._add_action(m_tools, "🖼  " + _("Tampon image…"), self._add_image_stamp)
        self._add_action(m_tools, "⚡  " + _("Compresser le PDF"), self._compress_pdf)
        m_tools.addSeparator()
        self._add_action(m_tools, "🔒  " + _("Protéger par mot de passe…"), self._protect_pdf)
        self._add_action(m_tools, "🔓  " + _("Supprimer la protection…"), self._unlock_pdf)
        m_tools.addSeparator()
        self._add_action(m_tools, "✍  " + _("Signer le document…"), self._sign_document)
        self._add_action(m_tools, "🔎  " + _("Vérifier les signatures…"), self._verify_signatures)
        m_tools.addSeparator()
        self._add_action(m_tools, "↻  " + _("Tourner la page (+90°)"), lambda: self._rotate_current(90), "R")
        self._add_action(m_tools, "↺  " + _("Tourner la page (-90°)"), lambda: self._rotate_current(-90), "Shift+R")
        m_tools.addSeparator()
        self._add_action(m_tools, "🔍  " + _("Recherche…"), self._open_search)
        self._add_action(m_tools, "🔤  " + _("Reconnaissance de caractères (OCR)…"), self._open_ocr)

        # Aide
        m_help = mb.addMenu(_("Aide"))
        self._add_action(m_help, "📖  " + _("Manuel utilisateur"), self._open_help, "F1")
        m_help.addSeparator()
        self._add_action(m_help, "🔑  " + _("Comment obtenir un certificat .pfx ?"), self._help_pfx)
        m_help.addSeparator()
        self._add_action(m_help, "🖥  " + _("Intégration Windows (clic droit)…"), self._shell_integration)
        self._add_action(m_help, "🔑  " + _("Licence…"), self._manage_license)
        m_help.addSeparator()
        self._add_action(m_help, "🐛  " + _("Signaler un bug…"), self._report_bug)
        self._add_action(m_help, "💡  " + _("Suggérer une amélioration…"), self._suggest_feature)
        m_help.addSeparator()
        self._add_action(m_help, "ℹ  " + _("À propos"), self._about)

    # ------------------------------------------------------------------
    # Connect signals
    # ------------------------------------------------------------------

    def _connect_signals(self) -> None:
        # Main toolbar
        self._main_toolbar.action_open.connect(self.open_file_dialog)
        self._main_toolbar.action_save.connect(self.save_file)
        self._main_toolbar.action_save_as.connect(self.save_file_as)
        self._main_toolbar.action_prev.connect(self._viewer.prev_page)
        self._main_toolbar.action_next.connect(self._viewer.next_page)
        self._main_toolbar.action_goto.connect(self._viewer.display_page)
        self._main_toolbar.action_zoom_in.connect(self._viewer.zoom_in)
        self._main_toolbar.action_zoom_out.connect(self._viewer.zoom_out)
        self._main_toolbar.action_zoom_fit.connect(self._viewer.zoom_fit_page)
        self._main_toolbar.action_zoom_width.connect(self._viewer.zoom_fit_width)
        self._main_toolbar.action_zoom_value.connect(self._viewer.set_zoom)
        self._main_toolbar.action_toggle_sidebar.connect(self._toggle_sidebar)

        # Viewer
        self._viewer.page_changed.connect(self._on_page_changed)
        self._viewer.zoom_changed.connect(self._on_zoom_changed)
        self._viewer._page_widget.annotation_drawn.connect(self._on_annotation_drawn)
        self._viewer._page_widget.annotation_erase_requested.connect(self._on_annotation_erase_requested)
        self._viewer._page_widget.comment_edit_requested.connect(self._on_comment_edit)
        self._viewer._page_widget.comment_moved.connect(self._on_comment_moved)
        self._viewer.annotation_moved.connect(self._on_annotation_moved)
        self._viewer.annotation_selected.connect(
            lambda ann: self.__setattr__("_last_deletable", {"type": "annotation", "ann": ann})
        )
        self._viewer._page_widget.text_edit_requested.connect(self._on_text_edit_requested)
        self._viewer.text_edit_confirmed.connect(self._on_text_edit_confirmed)  # (rect, text, fmt)
        self._viewer.text_selected.connect(self._on_text_selected)
        self._viewer.image_click_requested.connect(self._on_image_click)
        self._viewer.image_draw_requested.connect(self._on_image_draw_requested)
        self._viewer.image_context_requested.connect(self._on_image_context)
        self._viewer.image_overlay_confirmed.connect(self._on_image_overlay_confirmed)
        self._viewer.image_overlay_cancelled.connect(self._on_image_overlay_cancelled)
        self._viewer.block_pick_requested.connect(self._on_block_pick_requested)
        self._viewer.block_move_requested.connect(self._on_block_move_requested)

        # Sidebar
        self._sidebar.page_selected.connect(self._viewer.display_page)

        # Left tool panel (replaces annotation toolbar + properties bar)
        self._left_tool_panel.tool_selected.connect(self._on_tool_changed)
        self._left_tool_panel.color_changed.connect(self._set_color)
        self._left_tool_panel.stroke_width_changed.connect(self._set_stroke)
        self._left_tool_panel.action_triggered.connect(self._on_panel_action)

        # Language panel
        self._lang_panel.language_selected.connect(self._change_language)

        # Help panel
        self._help_panel.open_manual_requested.connect(self._open_help)
        self._help_panel.open_shell_int_requested.connect(self._shell_integration)

        # Context menu
        self._viewer.context_menu_requested.connect(self._on_context_menu)

        # Search
        self._search_panel.result_selected.connect(self._on_search_result)
        self._search_panel.close_requested.connect(self._search_dock.hide)

        # OCR
        self._ocr_panel.request_current_image.connect(self._provide_image_to_ocr)
        self._ocr_panel.overlay_requested.connect(self._on_ocr_overlay_requested)
        self._ocr_panel.ocr_lines_ready.connect(self._on_ocr_lines_ready)
        self._ocr_panel.preview_settings_changed.connect(self._on_ocr_preview_settings_changed)
        self._ocr_panel.close_requested.connect(self._on_ocr_close_requested)
        self._viewer.ocr_overlay_changed.connect(self._on_ocr_overlay_resized)

        # Form designer
        self._form_panel.new_form_requested.connect(self._new_blank_form)
        self._form_panel.design_mode_toggled.connect(self._on_form_design_mode)
        self._viewer.form_field_drawn.connect(self._on_form_field_drawn)
        self._viewer.form_element_moved.connect(self._on_form_element_moved)
        self._viewer.page_changed.connect(self._update_form_overlays)

        # Pages toolbar
        self._pages_toolbar.action_merge.connect(self._organize_pages)
        self._pages_toolbar.action_split.connect(self._split_pdf)
        self._pages_toolbar.action_delete_page.connect(self._delete_current_page)
        self._pages_toolbar.action_form_design.connect(self._on_form_design_mode)
        self._pages_toolbar.action_insert_image.connect(
            lambda: self._viewer.set_tool("image")
        )
        self._pages_toolbar.action_insert_text.connect(
            lambda: self._on_form_design_mode(True)
        )

    # ------------------------------------------------------------------
    # File operations
    # ------------------------------------------------------------------

    def _confirm_discard_changes(self) -> bool:
        """If the document has unsaved changes, ask the user what to do.

        Returns True if the caller may proceed (saved or discarded),
        False if the user cancelled.
        """
        if not (self._document.is_open and self._document.info.is_modified):
            return True
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Icon.Question)
        box.setWindowTitle(_("Modifications non enregistrées"))
        box.setText(_("Le document a été modifié. Enregistrer avant de continuer ?"))
        btn_save    = box.addButton(_("Enregistrer"),  QMessageBox.ButtonRole.AcceptRole)
        btn_discard = box.addButton(_("Ne pas enregistrer"), QMessageBox.ButtonRole.DestructiveRole)
        btn_cancel  = box.addButton(_("Annuler"),      QMessageBox.ButtonRole.RejectRole)
        box.setDefaultButton(btn_save)
        box.exec()
        clicked = box.clickedButton()
        if clicked == btn_save:
            self.save_file()
            return True
        if clicked == btn_discard:
            return True
        return False  # Cancel / fermeture de la boîte

    def open_file_dialog(self, _checked=None) -> None:
        if not self._confirm_discard_changes():
            return
        path, _filt = QFileDialog.getOpenFileName(
            self, _("Ouvrir un PDF"), "", _("PDF (*.pdf);;Tous les fichiers (*)")
        )
        if path:
            self.open_file(path)

    def open_file(self, path: str, password: str = "") -> None:
        if not self._confirm_discard_changes():
            return
        try:
            self._document.load(path, password)
        except ValueError:
            # File requires a user password to open — ask for it
            pw, ok = QInputDialog.getText(
                self, _("Fichier protégé"),
                _("Ce fichier est chiffré. Entrez le mot de passe pour l'ouvrir :"),
                QLineEdit.EchoMode.Password, "",
            )
            if not ok or not pw:
                return
            try:
                self._document.load(path, pw)
            except Exception as e:
                QMessageBox.critical(self, _("Erreur"), _("Impossible d'ouvrir le fichier :\n{err}").format(err=e))
                return
        except Exception as e:
            QMessageBox.critical(self, _("Erreur"), _("Impossible d'ouvrir le fichier :\n{err}").format(err=e))
            return

        try:
            self._renderer.load(path, self._document._password or "")
            self._annotations.load_from_pdf(self._document.pdf)
            self._history.clear()
            self._cache.clear()
            self._cleanup_edit_tempfile()
            self._edit_chain.clear()
            self._search_panel.set_document(path)
            self._form_manager.attach(self._document.pdf)
            self._form_panel.load_form(self._form_manager)
            self._update_form_overlays()
            if self._form_manager.has_form():
                self._right_dock.show()
            self._sidebar.load_thumbnails(self._renderer)
            self._viewer.display_page(0)
            self._config.add_recent_file(path)
            self._refresh_recent_menu()
            self._update_title()
            self._update_actions()
            msg = _("Ouvert : {name}").format(name=os.path.basename(path))
            if self._document.needs_owner_password:
                msg += _("  [lecture seule — mot de passe requis pour modifier]")
            if self._form_manager.has_form():
                n = len(self._form_manager.get_fields())
                msg += _("   📋 Formulaire : {n} champ(s)").format(n=n)
            self._status.showMessage(msg)
        except Exception as e:
            QMessageBox.critical(self, _("Erreur"), _("Impossible d'ouvrir le fichier :\n{err}").format(err=e))

    def save_file(self) -> None:
        if not self._document.is_open:
            return
        target = self._document.path
        if not target:
            return self.save_file_as()
        try:
            import io as _io, gc as _gc
            self._annotations.write_to_pdf(self._document.pdf)
            # Serialise the entire document to an in-memory buffer FIRST,
            # while all handles are still valid.
            buf = _io.BytesIO()
            self._document.pdf.save(buf)
            pdf_bytes = buf.getvalue()
            pwd = self._document._password or ""
            # Close EVERY handle that could keep the target file locked on Windows:
            #   • pdfium memory-maps the file it rendered from
            #   • pikepdf/libqpdf may also hold a read handle
            self._renderer.close()
            self._document.pdf.close()
            _gc.collect()           # force C-level cleanup of any lingering handles
            # Write to disk — all handles released.
            with open(target, "wb") as _fh:
                _fh.write(pdf_bytes)
            # Reopen everything from the freshly written file.
            self._document.reopen(target, pwd)
            self._form_manager.attach(self._document.pdf)
            self._renderer.load(target)
            self._cleanup_edit_tempfile()
            self._edit_chain.clear()
            self._viewer.refresh()
            self._refresh_annotations_overlay(self._viewer.current_page)
            self._document.info.is_modified = False
            self._update_title()
            self._status.showMessage(_("Fichier enregistré."))
        except Exception as e:
            QMessageBox.critical(self, _("Erreur"), str(e))

    def save_file_as(self) -> None:
        if not self._document.is_open:
            return
        default_dir = os.path.dirname(self._document.path) if self._document.path else ""
        path, _filt = QFileDialog.getSaveFileName(
            self, _("Enregistrer sous…"), default_dir, _("PDF (*.pdf)")
        )
        if path:
            try:
                self._annotations.write_to_pdf(self._document.pdf)
                self._document.save(path)
                self._status.showMessage(_("Enregistré sous : {path}").format(path=path))
            except Exception as e:
                QMessageBox.critical(self, _("Erreur"), str(e))

    def close_document(self) -> None:
        if not self._confirm_discard_changes():
            return
        self._cleanup_edit_tempfile()
        self._edit_chain.clear()
        self._document.close()
        self._renderer.close()
        self._annotations.clear()
        self._history.clear()
        self._cache.clear()
        self._sidebar.clear()
        self._viewer._page_widget.set_image(None)
        self._update_title()
        self._update_actions()
        self._status.showMessage(_("Document fermé."))

    # ------------------------------------------------------------------
    # Navigation / Zoom callbacks
    # ------------------------------------------------------------------

    def _on_page_changed(self, index: int) -> None:
        total = self._document.page_count
        self._main_toolbar.update_page_info(index, total)
        self._sidebar.select_page(index)
        self._status.showMessage(_("Page {page} / {total}").format(page=index + 1, total=total))
        # Refresh annotation overlay
        self._refresh_annotations_overlay(index)
        # Feed image to OCR panel if visible
        if not self._ocr_dock.isHidden():
            self._provide_image_to_ocr()

    def _on_zoom_changed(self, zoom: float) -> None:
        self._main_toolbar.update_zoom(zoom)
        if self._document.is_open:
            self._refresh_annotations_overlay(self._viewer.current_page)

    # ------------------------------------------------------------------
    # Annotations
    # ------------------------------------------------------------------

    def _on_text_selected(self, norm_rect: QRectF) -> None:
        """Extract text within the selection rect and copy it to clipboard."""
        if not self._document.is_open:
            return
        page_idx = self._viewer.current_page
        try:
            import pdfplumber
            with pdfplumber.open(self._document.path) as pdf:
                if page_idx >= len(pdf.pages):
                    return
                page = pdf.pages[page_idx]
                pw, ph = page.width, page.height
                x0 = norm_rect.x() * pw
                y0 = norm_rect.y() * ph
                x1 = (norm_rect.x() + norm_rect.width()) * pw
                y1 = (norm_rect.y() + norm_rect.height()) * ph
                cropped = page.within_bbox((x0, y0, x1, y1))
                text = cropped.extract_text() or ""
        except Exception:
            text = ""

        if text.strip():
            QApplication.clipboard().setText(text)
            snippet = text[:60] + ("…" if len(text) > 60 else "")
            self.statusBar().showMessage(
                _("Texte copié : « {snippet} »").format(snippet=snippet), 4000
            )
        else:
            self.statusBar().showMessage(_("Aucun texte trouvé dans la sélection."), 3000)

    def _on_image_click(self, norm_x: float, norm_y: float) -> None:
        """User clicked with image tool — find the image, show delete/replace dialog."""
        if not self._document.is_open:
            return
        if not self._ensure_owner_access():
            return

        from core.tools import PDFTools
        page_idx = self._viewer.current_page
        # Use the renderer's temp file when available — it reflects in-memory edits
        _query_path = getattr(self, "_edit_tempfile", None) or self._document.path
        images = PDFTools.get_images_on_page(_query_path, page_idx)

        # Find the image under the click (with small tolerance)
        clicked_img = None
        TOL = 0.01
        for img in images:
            if (img["x"] - TOL <= norm_x <= img["x"] + img["width"] + TOL and
                    img["y"] - TOL <= norm_y <= img["y"] + img["height"] + TOL):
                clicked_img = img
                break

        if clicked_img is None:
            # No image at click → treat as "add new image" at that position
            default_rect = QRectF(
                max(0.0, norm_x - 0.10), max(0.0, norm_y - 0.10), 0.20, 0.20
            )
            self._on_image_draw_requested(default_rect)
            return

        xobj_name = clicked_img["name"]
        # Store for overlay positioning
        self._last_clicked_img = clicked_img

        # Dialog: Delete or Replace
        msg = QMessageBox(self)
        msg.setWindowTitle(_("Image PDF"))
        msg.setText(_("Image détectée : « {name} »\nQue souhaitez-vous faire ?").format(name=xobj_name))
        btn_del = msg.addButton(_("Supprimer"), QMessageBox.ButtonRole.DestructiveRole)
        btn_rep = msg.addButton(_("Remplacer…"), QMessageBox.ButtonRole.AcceptRole)
        msg.addButton(_("Annuler"), QMessageBox.ButtonRole.RejectRole)
        msg.exec()

        clicked = msg.clickedButton()
        if clicked == btn_del:
            self._image_delete(page_idx, xobj_name)
        elif clicked == btn_rep:
            self._image_replace(page_idx, xobj_name)

    def _on_image_context(self, norm_x: float, norm_y: float) -> None:
        """Right-click anywhere on the page — unified context menu."""
        if not self._document.is_open:
            return

        from PySide6.QtGui import QCursor
        from PySide6.QtWidgets import QMenu

        page_idx = self._viewer.current_page

        # ── Qt annotations (highlights, freetext, comment, image annotations) ──
        ann = self._viewer.annotation_at_norm(norm_x, norm_y)
        if ann:
            self._on_context_menu(ann, QCursor.pos().x(), QCursor.pos().y())
            return

        if not self._ensure_owner_access():
            return

        # ── Injected block (_BEGIN_PDFED) ─────────────────────────────────
        from core.block_detector import get_injected_block_at
        inj = get_injected_block_at(self._document.pdf, page_idx, norm_x, norm_y)
        if inj:
            menu = QMenu(self)
            menu.addAction(
                _("Modifier le texte…"),
                lambda: self._on_text_edit_requested(
                    inj.norm_x + inj.norm_w / 2, inj.norm_y + inj.norm_h / 2
                ),
            )
            menu.addSeparator()
            menu.addAction(
                _("Supprimer ce bloc"),
                lambda: self._delete_injected_block(page_idx, inj.block_id),
            )
            menu.exec(QCursor.pos())
            return

        # ── Form label / texte block ─────────────────────────────────────
        label = self._form_manager.get_label_at(page_idx, norm_x, norm_y)
        if label:
            menu = QMenu(self)
            menu.addAction(
                _("Modifier le texte…"),
                lambda: self._on_text_edit_requested(norm_x, norm_y),
            )
            menu.addAction(
                _("Supprimer"),
                lambda: self._label_delete(page_idx, label["name"]),
            )
            menu.exec(QCursor.pos())
            return

        # ── AcroForm field (text input, checkbox, radio, dropdown) ───────
        overlays = self._form_manager.get_form_overlays_for_page(page_idx)
        hit_field = None
        _TOL = 0.01
        for ov in overlays:
            if (ov["nx"] - _TOL <= norm_x <= ov["nx"] + ov["nw"] + _TOL and
                    ov["ny"] - _TOL <= norm_y <= ov["ny"] + ov["nh"] + _TOL):
                hit_field = ov
                break
        if hit_field:
            _fname = hit_field["name"]
            _ftype = hit_field.get("type", "text")
            menu = QMenu(self)
            menu.addAction(
                _("Modifier le champ « {name} »…").format(name=_fname),
                lambda n=_fname, t=_ftype: self._field_edit(n, t),
            )
            menu.addAction(
                _("Supprimer le champ « {name} »").format(name=_fname),
                lambda n=_fname: self._field_delete(n),
            )
            menu.exec(QCursor.pos())
            return

        # ── Native PDF text block (stream content, not annotation) ──────
        from core.block_detector import get_block_at as _get_native_blk
        _native = _get_native_blk(self._document.pdf, page_idx, norm_x, norm_y)
        if _native:
            import pikepdf as _pk_ctx
            _page_ctx = self._document.pdf.pages[page_idx]
            _mb_ctx = _page_ctx.get("/MediaBox", _pk_ctx.Array([0, 0, 595, 842]))
            _pw_ctx = float(_mb_ctx[2]) - float(_mb_ctx[0])
            _ph_ctx = float(_mb_ctx[3]) - float(_mb_ctx[1])
            _blk_nr_ctx = _native.norm_rect(_pw_ctx, _ph_ctx)
            menu = QMenu(self)
            _preview = _native.text[:40].replace("\n", " ")
            menu.addAction(
                _("Modifier « {t}… »").format(t=_preview),
                lambda: self._on_text_edit_requested(norm_x, norm_y),
            )
            menu.addSeparator()
            menu.addAction(
                _("Masquer (rectangle blanc)"),
                lambda blk=_native, nr=_blk_nr_ctx, ph=_ph_ctx: self._hide_native_text(page_idx, blk, nr, ph),
            )
            menu.addAction(
                _("Supprimer du flux PDF"),
                lambda blk=_native: self._delete_native_text(page_idx, blk),
            )
            menu.exec(QCursor.pos())
            return

        # ── PDF image ────────────────────────────────────────────────────
        from core.tools import PDFTools
        _query_path = getattr(self, "_edit_tempfile", None) or self._document.path
        images = PDFTools.get_images_on_page(_query_path, page_idx)

        clicked_img = None
        TOL = 0.01
        for img in images:
            if (img["x"] - TOL <= norm_x <= img["x"] + img["width"] + TOL and
                    img["y"] - TOL <= norm_y <= img["y"] + img["height"] + TOL):
                clicked_img = img
                break

        if clicked_img is None:
            return  # nothing under cursor — right-click is ignored

        xobj_name = clicked_img["name"]
        self._last_clicked_img = clicked_img

        msg = QMessageBox(self)
        msg.setWindowTitle(_("Image PDF"))
        msg.setText(_("Image détectée : « {name} »\nQue souhaitez-vous faire ?").format(name=xobj_name))
        btn_del = msg.addButton(_("Supprimer"), QMessageBox.ButtonRole.DestructiveRole)
        btn_rep = msg.addButton(_("Remplacer…"), QMessageBox.ButtonRole.AcceptRole)
        btn_mv  = msg.addButton(_("Déplacer / redimensionner…"), QMessageBox.ButtonRole.ActionRole)
        msg.addButton(_("Annuler"), QMessageBox.ButtonRole.RejectRole)
        msg.exec()

        clicked = msg.clickedButton()
        if clicked == btn_del:
            self._image_delete(page_idx, xobj_name)
        elif clicked == btn_rep:
            self._image_replace(page_idx, xobj_name)
        elif clicked == btn_mv:
            self._image_move(page_idx, xobj_name, clicked_img)

    def _label_delete(self, page_idx: int, name: str) -> None:
        """Remove a label/texte annotation and refresh the view."""
        self._form_manager.remove_label(page_idx, name)
        self._reload_renderer_from_doc()
        self._viewer.refresh()
        self._update_form_overlays()
        self._form_panel.load_form(self._form_manager)
        self._document.info.is_modified = True
        self._update_title()

    def _field_delete(self, name: str) -> None:
        """Remove an AcroForm field and refresh the view."""
        self._form_manager.remove_field(name)
        self._reload_renderer_from_doc()
        self._viewer.refresh()
        self._update_form_overlays()
        self._form_panel.load_form(self._form_manager)
        self._document.info.is_modified = True
        self._update_title()

    def _field_edit(self, name: str, ftype: str) -> None:
        """Open edit dialog for an existing AcroForm field and rebuild it."""
        from ui.dialogs.edit_field_dialog import EditFieldDialog
        defs = self._form_manager.get_field_definitions()
        current = next((d for d in defs if d["name"] == name), None)

        # For checkboxes that belong to a group, reconstruct group name and options
        if ftype == "checkbox" and current and current.get("group"):
            group_name = current["group"]
            current_options = [
                d["option"] for d in defs
                if d.get("type") == "checkbox" and d.get("group") == group_name
            ]
            edit_name = group_name
        else:
            group_name = None
            current_options = current.get("options", []) if current else []
            edit_name = name

        dlg = EditFieldDialog(edit_name, ftype, current_options, self)
        if dlg.exec() != EditFieldDialog.DialogCode.Accepted:
            return

        new_name = dlg.field_name()
        new_options = dlg.field_options()
        if not new_name:
            return

        # Check name conflict if renamed
        if new_name != edit_name and self._form_manager.field_name_exists(new_name):
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                _("Nom déjà utilisé"),
                _("Un champ nommé « {name} » existe déjà.").format(name=new_name),
            )
            return

        # Find position from overlays (use the clicked widget's position as reference)
        page_idx = self._viewer.current_page
        overlays = self._form_manager.get_form_overlays_for_page(page_idx)
        if group_name:
            # For checkbox group: find the leftmost sibling to get the full rect
            siblings = [o for o in overlays if o["name"].startswith(f"{group_name}_")]
            if not siblings:
                return
            nx  = min(o["nx"] for o in siblings)
            ny  = min(o["ny"] for o in siblings)
            nw  = sum(o["nw"] / 0.85 for o in siblings)  # reverse slot_w * 0.85
            nh  = max(o["nh"] for o in siblings)
        else:
            ov = next((o for o in overlays if o["name"] == name), None)
            if ov is None:
                return
            nx, ny, nw, nh = ov["nx"], ov["ny"], ov["nw"], ov["nh"]

        from PySide6.QtCore import QRectF
        norm_rect = QRectF(nx, ny, nw, nh)

        # Rebuild: delete old, create new
        if group_name:
            self._form_manager.remove_checkbox_group(group_name)
        else:
            self._form_manager.remove_field(name)
        self._form_manager.add_field(new_name, ftype, norm_rect, page_idx, new_options)
        self._reload_renderer_from_doc()
        self._viewer.refresh()
        self._update_form_overlays()
        self._form_panel.load_form(self._form_manager)
        self._document.info.is_modified = True
        self._update_title()

    def _image_move(self, page_idx: int, xobj_name: str, img_info: dict) -> None:
        """Re-open the overlay on an already-placed image to move/resize it."""
        try:
            import pikepdf
            from PIL import Image as PilImage
            pdf  = self._document.pdf
            page = pdf.pages[page_idx]
            xobjects = page.Resources.get("/XObject", {})
            xobj = xobjects.get(f"/{xobj_name}")
            if xobj is None:
                return
            # Reconstruct a PIL image from the XObject raw bytes
            w_px = int(xobj.get("/Width", 64))
            h_px = int(xobj.get("/Height", 64))
            raw  = xobj.read_raw_bytes()
            try:
                src_img = PilImage.frombytes("RGB", (w_px, h_px), raw)
            except Exception:
                src_img = PilImage.new("RGB", (w_px, h_px), (128, 128, 128))

            norm_rect = QRectF(
                img_info["x"], img_info["y"],
                img_info["width"], img_info["height"],
            )
            self._pending_replace = (page_idx, xobj_name, src_img)
            self._last_clicked_img = img_info
            self._viewer.show_image_overlay(src_img, norm_rect)
            self.statusBar().showMessage(
                _("Redimensionnez / déplacez l'image puis cliquez ✓ Valider."), 0
            )
        except Exception as exc:
            QMessageBox.warning(self, _("Erreur"), str(exc))

    def _insert_image_from_menu(self) -> None:
        """Menu 'Insérer une image…' : ouvre directement le sélecteur de fichier
        puis place l'image au centre de la page courante."""
        if not self._document.is_open:
            return
        if not self._ensure_owner_access():
            return
        # Centre de la page, taille 30% de la largeur
        default_rect = QRectF(0.35, 0.35, 0.30, 0.30)
        self._on_image_draw_requested(default_rect)

    def _on_image_draw_requested(self, norm_rect: QRectF) -> None:
        """User drew a rectangle with Image tool → insert a new image there."""
        if not self._document.is_open:
            return
        if not self._ensure_owner_access():
            return

        from PIL import Image as PilImage
        default_dir = os.path.dirname(self._document.path) if self._document.path else ""
        new_path, _filt = QFileDialog.getOpenFileName(
            self, _("Choisir une image à insérer"), default_dir,
            _("Images (*.png *.jpg *.jpeg *.bmp *.tiff *.webp)"),
        )
        if not new_path:
            return

        try:
            _raw = PilImage.open(new_path)
            src_img = _raw.convert("RGBA") if _raw.mode in ("RGBA", "LA", "PA") else _raw.convert("RGB")
        except Exception as exc:
            QMessageBox.warning(self, _("Erreur"), _("Impossible de lire l'image :\n{err}").format(err=exc))
            return

        # Generate a unique XObject name
        import pikepdf
        page_idx = self._viewer.current_page
        page = self._document.pdf.pages[page_idx]
        xobjects = page.Resources.get("/XObject", pikepdf.Dictionary())
        existing = set(str(k) for k in xobjects.keys())
        n = 1
        while f"/NewImg{n}" in existing:
            n += 1
        xobj_name = f"NewImg{n}"

        # Add placeholder XObject so the name exists (overlay will fill it in)
        placeholder = pikepdf.Stream(self._document.pdf, b"")
        placeholder["/Type"]    = pikepdf.Name("/XObject")
        placeholder["/Subtype"] = pikepdf.Name("/Image")
        placeholder["/Width"]   = pikepdf.Integer(1)
        placeholder["/Height"]  = pikepdf.Integer(1)
        placeholder["/ColorSpace"]       = pikepdf.Name("/DeviceRGB")
        placeholder["/BitsPerComponent"] = pikepdf.Integer(8)
        xobjects[f"/{xobj_name}"] = placeholder
        if "/XObject" not in page.Resources:
            page.Resources["/XObject"] = xobjects

        # Store and show overlay — reuse replace flow
        self._pending_replace = (page_idx, xobj_name, src_img)
        self._last_clicked_img = {
            "name": xobj_name,
            "x": norm_rect.x(), "y": norm_rect.y(),
            "width": norm_rect.width(), "height": norm_rect.height(),
        }
        self._viewer.show_image_overlay(src_img, norm_rect)
        self.statusBar().showMessage(
            _("Redimensionnez / déplacez l'image puis cliquez ✓ Valider."), 0
        )

    def _image_delete(self, page_idx: int, xobj_name: str) -> None:
        """Delete image by removing its drawing commands from the content stream.
        The underlying content (text, graphics) is fully preserved."""
        try:
            import pikepdf
            pdf  = self._document.pdf
            page = pdf.pages[page_idx]
            do_name      = pikepdf.Name(f"/{xobj_name}")
            instructions = list(pikepdf.parse_content_stream(page))

            # Remove the q … cm … Do … Q block that draws this image
            modified = []
            i = 0
            while i < len(instructions):
                ops, op = instructions[i]
                if op == pikepdf.Operator("Do") and ops and ops[0] == do_name:
                    # Walk back through modified[] to find the opening q (respecting nesting)
                    q_idx = -1
                    depth = 0
                    for j in range(len(modified) - 1, -1, -1):
                        m_ops, m_op = modified[j]
                        if m_op == pikepdf.Operator("Q"):
                            depth += 1
                        elif m_op == pikepdf.Operator("q"):
                            if depth == 0:
                                q_idx = j
                                break
                            depth -= 1
                    if q_idx >= 0:
                        del modified[q_idx:]   # remove q + cm (and any intermediate ops)
                    # Skip the Do itself and the closing Q
                    i += 1
                    if i < len(instructions) and instructions[i][1] == pikepdf.Operator("Q"):
                        i += 1
                    continue
                modified.append((ops, op))
                i += 1

            page.Contents = pikepdf.Stream(pdf, pikepdf.unparse_content_stream(modified))
            self._document.info.is_modified = True
            self._reload_renderer_from_doc()
            self._viewer.refresh()
            self.statusBar().showMessage(_("Image supprimée."), 3000)
        except Exception as exc:
            QMessageBox.warning(self, _("Erreur"), _("Impossible de lire l'image :\n{err}").format(err=exc))

    def _image_replace(self, page_idx: int, xobj_name: str) -> None:
        """Replace image XObject — shows a live overlay on the PDF for resizing."""
        from PIL import Image as PilImage

        default_dir = os.path.dirname(self._document.path) if self._document.path else ""
        new_path, _filt = QFileDialog.getOpenFileName(
            self, _("Choisir une image de remplacement"), default_dir,
            _("Images (*.png *.jpg *.jpeg *.bmp *.tiff *.webp)"),
        )
        if not new_path:
            return

        try:
            _raw = PilImage.open(new_path)
            src_img = _raw.convert("RGBA") if _raw.mode in ("RGBA", "LA", "PA") else _raw.convert("RGB")
        except Exception as exc:
            QMessageBox.warning(self, _("Erreur"), _("Impossible de lire l'image :\n{err}").format(err=exc))
            return

        # Build norm_rect from last clicked image info
        img_info = getattr(self, "_last_clicked_img", None)
        if img_info:
            from PySide6.QtCore import QRectF
            norm_rect = QRectF(
                img_info["x"], img_info["y"],
                img_info["width"], img_info["height"],
            )
        else:
            norm_rect = QRectF(0.1, 0.1, 0.3, 0.3)

        # Store pending replace info for when overlay is confirmed
        self._pending_replace = (page_idx, xobj_name, src_img)

        self._viewer.show_image_overlay(src_img, norm_rect)
        self.statusBar().showMessage(
            _("Redimensionnez l'image puis cliquez ✓ Valider."), 0
        )

    def _on_image_overlay_confirmed(
        self,
        target_w: int, target_h: int,
        norm_x: float, norm_y: float, norm_w: float, norm_h: float,
    ) -> None:
        """Apply replacement: XObject + move drawing to end of stream (on top)."""
        pending = getattr(self, "_pending_replace", None)
        if pending is None:
            return
        page_idx, xobj_name, src_img = pending
        self._pending_replace = None
        self.statusBar().clearMessage()

        try:
            from PIL import Image as PilImage
            import pikepdf

            pdf  = self._document.pdf
            page = pdf.pages[page_idx]

            # ── 1. Build replacement XObject (with optional SMask for alpha) ──
            xobjects = page.Resources.get("/XObject", {})
            key = f"/{xobj_name}"
            if key not in xobjects:
                raise KeyError(f"XObject {key} introuvable.")

            has_alpha = src_img.mode in ("RGBA", "LA", "PA")
            if has_alpha:
                resized_rgba = src_img.convert("RGBA").resize(
                    (target_w, target_h), PilImage.LANCZOS
                )
                rgb_img   = resized_rgba.convert("RGB")
                alpha_img = resized_rgba.split()[3]          # grayscale alpha
            else:
                rgb_img   = src_img.convert("RGB").resize(
                    (target_w, target_h), PilImage.LANCZOS
                )
                alpha_img = None

            new_xobj = pikepdf.Stream(pdf, rgb_img.tobytes())
            new_xobj["/Type"]             = pikepdf.Name("/XObject")
            new_xobj["/Subtype"]          = pikepdf.Name("/Image")
            new_xobj["/Width"]            = pikepdf.Integer(target_w)
            new_xobj["/Height"]           = pikepdf.Integer(target_h)
            new_xobj["/ColorSpace"]       = pikepdf.Name("/DeviceRGB")
            new_xobj["/BitsPerComponent"] = pikepdf.Integer(8)

            if alpha_img is not None:
                smask = pikepdf.Stream(pdf, alpha_img.tobytes())
                smask["/Type"]             = pikepdf.Name("/XObject")
                smask["/Subtype"]          = pikepdf.Name("/Image")
                smask["/Width"]            = pikepdf.Integer(target_w)
                smask["/Height"]           = pikepdf.Integer(target_h)
                smask["/ColorSpace"]       = pikepdf.Name("/DeviceGray")
                smask["/BitsPerComponent"] = pikepdf.Integer(8)
                new_xobj["/SMask"]         = smask   # direct object reference

            xobjects[key] = new_xobj

            # ── 2. Compute new CTM in PDF points ──────────────────────────
            mb   = page.MediaBox
            pw   = float(mb[2]) - float(mb[0])
            ph   = float(mb[3]) - float(mb[1])
            mb_x = float(mb[0])
            mb_y = float(mb[1])
            pdf_x = norm_x * pw + mb_x
            pdf_y = (1.0 - norm_y - norm_h) * ph + mb_y
            pdf_w = norm_w * pw
            pdf_h = norm_h * ph

            do_name      = pikepdf.Name(f"/{xobj_name}")
            instructions = list(pikepdf.parse_content_stream(page))

            # ── 3. Remove old q…Do…Q block, append at end (Z-order: on top) ─
            modified = []
            i = 0
            while i < len(instructions):
                ops, op = instructions[i]
                if op == pikepdf.Operator("Do") and ops and ops[0] == do_name:
                    # Find the opening q in modified (track nesting)
                    q_idx = -1
                    depth = 0
                    for j in range(len(modified) - 1, -1, -1):
                        m_ops, m_op = modified[j]
                        if m_op == pikepdf.Operator("Q"):
                            depth += 1
                        elif m_op == pikepdf.Operator("q"):
                            if depth == 0:
                                q_idx = j
                                break
                            depth -= 1
                    if q_idx >= 0:
                        del modified[q_idx:]   # remove q + cm + any ops before Do
                    # Skip the Do itself; also skip the closing Q if next
                    i += 1
                    if i < len(instructions):
                        nops, nop = instructions[i]
                        if nop == pikepdf.Operator("Q"):
                            i += 1
                    continue
                modified.append((ops, op))
                i += 1

            # Append new drawing at the very end → on top of text/graphics
            modified += [
                ([], pikepdf.Operator("q")),
                ([pikepdf.Real(pdf_w), pikepdf.Real(0),
                  pikepdf.Real(0),     pikepdf.Real(pdf_h),
                  pikepdf.Real(pdf_x), pikepdf.Real(pdf_y)],
                 pikepdf.Operator("cm")),
                ([do_name], pikepdf.Operator("Do")),
                ([], pikepdf.Operator("Q")),
            ]

            page.Contents = pikepdf.Stream(pdf, pikepdf.unparse_content_stream(modified))
            self._document.info.is_modified = True
            self._reload_renderer_from_doc()
            self._viewer.refresh()
            self.statusBar().showMessage(_("Image remplacée."), 3000)
        except Exception as exc:
            QMessageBox.warning(self, _("Erreur"), _("Impossible de lire l'image :\n{err}").format(err=exc))

    def _on_image_overlay_cancelled(self) -> None:
        self._pending_replace = None
        self.statusBar().clearMessage()

    def _on_annotation_drawn(self, ann_type: str, rect: QRectF) -> None:
        if not self._ensure_owner_access():
            return

        comment_text = ""
        if ann_type == "comment":
            text, ok = QInputDialog.getMultiLineText(
                self,
                _("Commentaire"),
                _("Saisir le commentaire :"),
                "",
            )
            if not ok:
                return
            comment_text = text.strip()

        ann = Annotation(
            page=self._viewer.current_page,
            type=ann_type,
            x=rect.x(), y=rect.y(),
            width=rect.width(), height=rect.height(),
            color=self._current_color,
            stroke_width=self._current_stroke,
            text=comment_text,
        )
        cmd = AnnotationAddCommand(self._annotations, ann, self._viewer)
        self._history.push(cmd)
        self._update_actions()

    def _on_comment_edit(self, ann_id: str) -> None:
        """Double-click on a comment annotation: open dialog to edit its text."""
        page = self._viewer.current_page
        ann = next(
            (a for a in self._annotations.get_page_annotations(page) if a.id == ann_id),
            None,
        )
        if ann is None:
            return
        text, ok = QInputDialog.getMultiLineText(
            self,
            _("Modifier le commentaire"),
            _("Saisir le commentaire :"),
            ann.text,
        )
        if not ok:
            return
        ann.text = text.strip()
        self._refresh_annotations_overlay(page)
        self._update_actions()

    def _on_comment_moved(self, ann_id: str, new_x: float, new_y: float) -> None:
        """Comment annotation was dragged to a new position: persist the new coords."""
        page = self._viewer.current_page
        ann = next(
            (a for a in self._annotations.get_page_annotations(page) if a.id == ann_id),
            None,
        )
        if ann is None:
            return
        ann.x = new_x
        ann.y = new_y
        self._update_actions()

    def _on_annotation_moved(self, ann_id: str, new_x: float, new_y: float) -> None:
        """Any annotation was moved in select mode — persist new position."""
        page = self._viewer.current_page
        ann = next(
            (a for a in self._annotations.get_page_annotations(page) if a.id == ann_id),
            None,
        )
        if ann is None:
            return
        ann.x = new_x
        ann.y = new_y
        self._document.info.is_modified = True
        self._update_title()
        self._update_actions()

    def _refresh_annotations_overlay(self, page: int) -> None:
        self._viewer._page_widget.clear_annotations()
        for ann in self._annotations.get_page_annotations(page):
            d = ann.to_dict()
            if hasattr(ann, "_extra_fmt"):
                d.update(ann._extra_fmt)
            self._viewer.add_annotation(d)

    def _on_annotation_erase_requested(self, sel: QRectF) -> None:
        """Erase all annotations whose bounding box intersects the selection rect."""
        page = self._viewer.current_page
        anns = self._annotations.get_page_annotations(page)
        pw = self._viewer._page_widget.width() or 1
        ph = self._viewer._page_widget.height() or 1
        # Use the same minimum icon size for comments as _comment_at() does.
        note_norm_size = 28 / min(pw, ph)
        def _ann_rect(ann) -> QRectF:
            if ann.type == "comment":
                w = max(ann.width, note_norm_size)
                h = max(ann.height, note_norm_size)
            else:
                w, h = ann.width, ann.height
            return QRectF(ann.x, ann.y, w, h)
        to_remove = [
            ann for ann in anns
            if sel.intersects(_ann_rect(ann))
        ]
        if not to_remove:
            self._status.showMessage(_("Aucune annotation dans la sélection."), 3000)
            return
        # Note: to_remove only contains overlay annotations (highlight, freetext, draw…)
        # added via this app; native PDF annotations are not listed here.
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Icon.Question)
        box.setWindowTitle(_("Effacer les annotations"))
        box.setText(_("Supprimer {n} annotation(s) sélectionnée(s) ?").format(n=len(to_remove)))
        btn_yes = box.addButton(_("Supprimer"), QMessageBox.ButtonRole.DestructiveRole)
        box.addButton(_("Annuler"), QMessageBox.ButtonRole.RejectRole)
        box.setDefaultButton(btn_yes)
        box.exec()
        if box.clickedButton() != btn_yes:
            return
        for ann in to_remove:
            self._annotations.remove(ann.id)
        self._refresh_annotations_overlay(page)
        self._status.showMessage(_("{n} annotation(s) effacée(s).").format(n=len(to_remove)))

    def _activate_move_block_tool(self) -> None:
        """Toggle the move_block tool on/off (from menu or shortcut M)."""
        if self._current_tool == "move_block":
            self._on_tool_changed("select")
            self._left_tool_panel.deselect_all()
        else:
            self._on_tool_changed("move_block")
            self._left_tool_panel.select_tool("move_block")

    def _on_tool_changed(self, tool: str) -> None:
        self._current_tool = tool
        self._viewer.set_tool(tool)

    def _set_color(self, color: str) -> None:
        self._current_color = color

    def _set_stroke(self, width: float) -> None:
        self._current_stroke = width

    # ------------------------------------------------------------------
    # Inline text editing
    # ------------------------------------------------------------------

    def _on_text_edit_requested(self, norm_x: float, norm_y: float) -> None:
        """User clicked in text_edit mode — find the word, resolve font, show editor."""
        if not self._document.is_open:
            return

        # If the click lands on a freetext overlay annotation (created via double-click),
        # open it for editing in place.
        _ann_hit = self._viewer.annotation_at_norm(norm_x, norm_y)
        if _ann_hit and _ann_hit.get("type") == "freetext":
            from PySide6.QtCore import QRectF as _QRectF
            self._editing_freetext_ann = _ann_hit
            self._editing_label = None
            self._last_edit_page = self._viewer.current_page
            self._last_word_info = {}
            self._viewer.show_text_editor(
                _QRectF(_ann_hit["x"], _ann_hit["y"],
                        _ann_hit.get("width", 0.25), _ann_hit.get("height", 0.04)),
                _ann_hit.get("text", ""),
                font_family=_ann_hit.get("font_family", "Arial"),
                font_size=_ann_hit.get("font_size", 12.0),
                bold=_ann_hit.get("bold", False),
                italic=_ann_hit.get("italic", False),
                color=_ann_hit.get("color", "#000000"),
                letter_spacing=_ann_hit.get("letter_spacing", 0.0),
                bg_color=_ann_hit.get("bg_color", ""),
            )
            return

        # If the click lands on a form label (FreeText annotation), edit it directly.
        label = self._form_manager.get_label_at(
            self._viewer.current_page, norm_x, norm_y
        )
        if label:
            from PySide6.QtCore import QRectF as _QRectF
            self._editing_label = label
            self._last_edit_page = self._viewer.current_page
            # Left-click selects this element → Del will delete it
            self._last_deletable = {"type": "label", "page_idx": self._viewer.current_page, "name": label["name"]}
            self._last_word_info = {}
            # Retrieve full formatting so the popup reflects current state
            fmt0 = self._form_manager.get_label_formatting(
                self._viewer.current_page, label["name"]
            )
            self._viewer.show_text_editor(
                _QRectF(label["nx"], label["ny"], label["nw"], label["nh"]),
                label["text"],
                font_family="Helvetica",
                font_size=fmt0.get("font_size", label.get("font_size", 12.0)),
                bold=fmt0.get("bold", False),
                italic=fmt0.get("italic", False),
                color=fmt0.get("color", "#000000"),
                underline=fmt0.get("underline", False),
                letter_spacing=fmt0.get("letter_spacing", 0.0),
                bg_color=fmt0.get("bg_color", ""),
            )
            return

        self._editing_label = None  # not editing a label annotation

        # If the page has OCR annotations, clicking outside an annotation rect must NOT
        # fall through to the native Stream 0 text editor — that would let the user
        # inadvertently edit the original content stream while thinking they edit OCR text.
        if self._form_manager.has_ocr_annotations(self._viewer.current_page):
            self._status.showMessage(
                _("Cliquez directement sur un bloc de texte OCR pour le modifier."), 3000
            )
            return

        if not self._ensure_owner_access():
            return
        from core.tools import PDFTools
        from utils.font_manager import find_best_family, can_download, is_font_available
        from ui.dialogs.font_download_dialog import FontDownloadDialog

        # Always read from the original on-disk file — pdfplumber is reliable there.
        # The edit chain resolves what the current text is for each word.
        word_info = PDFTools.get_word_at_position(
            self._document.path,
            self._viewer.current_page,
            norm_x, norm_y,
        )
        if word_info is None:
            # No text at click position → let user add a new text annotation
            from PySide6.QtCore import QRectF as _QRectF
            # Default box: small rectangle at click position
            _new_rect = _QRectF(norm_x - 0.01, norm_y - 0.015, 0.25, 0.04)
            self._viewer.show_text_editor(_new_rect, "", "Arial", 12)
            self._last_word_info = {
                "text": "",
                "norm_rect": {"x": _new_rect.x(), "y": _new_rect.y(),
                              "width": _new_rect.width(), "height": _new_rect.height()},
                "font_family": "Arial", "font_size": 12.0,
                "bold": False, "italic": False, "color": "#000000",
                "is_new_block": True,
            }
            self._last_edit_page = self._viewer.current_page
            return

        # Apply the edit chain: the original file still has the old text,
        # but the in-memory PDF (and renderer) have the current text.
        current_text = self._resolve_current_text(self._viewer.current_page, word_info["text"])
        if current_text != word_info["text"]:
            word_info = dict(word_info)   # shallow copy so we don't mutate the cached result
            word_info["text"] = current_text

        # Find the exact BT block (stream_index + bt_index) via block_detector so that
        # Strategy A can target the correct occurrence when the same text exists at multiple
        # positions (e.g. duplicated address columns).
        try:
            from core.block_detector import get_block_at as _get_block_at
            _blk = _get_block_at(
                self._document.pdf,
                self._viewer.current_page,
                norm_x, norm_y,
            )
            if _blk is not None:
                # Find the item in the block that matches the clicked word text
                # (prefer exact text match; among ties pick closest x to click)
                _page_obj = self._document.pdf.pages[self._viewer.current_page]
                _mb = _page_obj.get("/MediaBox")
                _pw = float(_mb[2]) - float(_mb[0]) if _mb else 595.0
                _ph = float(_mb[3]) - float(_mb[1]) if _mb else 842.0
                _click_x_pdf = norm_x * _pw
                _best_item = None
                _best_dist = float("inf")
                _word_text = word_info.get("text", "")
                for _line in _blk.lines:
                    for _item in _line.items:
                        if _word_text and _item.text != _word_text:
                            continue
                        _dist = abs(_item.x - _click_x_pdf)
                        if _dist < _best_dist:
                            _best_dist = _dist
                            _best_item = _item
                # Always make a copy before modifying word_info
                word_info = dict(word_info)
                # Store the full block bounding box so the cover rect covers
                # the entire original text (not just the clicked word).
                word_info["block_norm_rect"] = _blk.norm_rect(_pw, _ph)
                # Store font size of the top line for proper ascender margin
                word_info["block_font_size"] = _blk.font_size
                # Store the full block so Strategy B can delete it from the stream
                word_info["native_block"] = _blk
                if _best_item is not None:
                    word_info["stream_index"] = _best_item.stream_index
                    word_info["bt_index"] = _best_item.bt_index
        except Exception:
            pass  # non-critical: fall back to untargeted replacement

        # Store for use in _on_text_edit_confirmed
        self._last_word_info = word_info
        self._last_edit_page = self._viewer.current_page

        # --- Font resolution: exact match → equivalent → download proposition ---
        raw_font = word_info.get("font_name", "") or word_info.get("font_family", "Arial")
        best_family, is_exact, note = find_best_family(raw_font)

        if not is_exact and not is_font_available(best_family) and can_download(best_family):
            dlg = FontDownloadDialog(raw_font, best_family, note, self)
            if dlg.exec() == FontDownloadDialog.DialogCode.Accepted and dlg.success:
                best_family, is_exact, note = find_best_family(raw_font)
            else:
                best_family = "Arial"

        nr = word_info["norm_rect"]
        norm_rect = QRectF(nr["x"], nr["y"], nr["width"], nr["height"])
        suffix = f"  [{note}]" if not is_exact else ""
        bold_str = _("  Gras") if word_info['bold'] else ""
        italic_str = _("  Italique") if word_info['italic'] else ""
        self._status.showMessage(
            f"{_('Police : {info}').format(info=best_family)}  {word_info['font_size']:.0f}pt"
            f"{bold_str}{italic_str}"
            f"  {word_info['color']}{suffix}"
        )
        self._viewer.show_text_editor(
            norm_rect,
            word_info["text"],
            font_family=best_family,
            font_size=word_info["font_size"],
            bold=word_info["bold"],
            italic=word_info["italic"],
            color=word_info["color"],
        )

    def _on_text_edit_confirmed(self, norm_rect: QRectF, new_text: str, fmt: dict) -> None:
        """User confirmed text edit — try in-place stream edit, fall back to overlay."""
        # Freetext overlay annotation edit: update the dict in-place and refresh.
        if self._editing_freetext_ann is not None:
            ann = self._editing_freetext_ann
            self._editing_freetext_ann = None
            ann.update({
                "text": new_text or ann.get("text", ""),
                "x": norm_rect.x(), "y": norm_rect.y(),
                "width": norm_rect.width(), "height": norm_rect.height(),
                "color": fmt.get("color", "#000000"),
                "font_family": fmt.get("font_family", "Arial"),
                "font_size": fmt.get("font_size", 12.0),
                "font_size_ratio": fmt.get("font_size_ratio", 1.0),
                "bold": fmt.get("bold", False),
                "italic": fmt.get("italic", False),
                "underline": fmt.get("underline", False),
                "letter_spacing": fmt.get("letter_spacing", 0.0),
                "bg_color": fmt.get("bg_color", ""),
            })
            # Mirror the update in the AnnotationManager so the PDF save is consistent
            ann_id = ann.get("id")
            if ann_id:
                for _ao in self._annotations.get_page_annotations(self._last_edit_page):
                    if _ao.id == ann_id:
                        _ao.text = ann["text"]
                        _ao.x = ann["x"]; _ao.y = ann["y"]
                        _ao.width = ann["width"]; _ao.height = ann["height"]
                        _ao.color = ann["color"]
                        if hasattr(_ao, "_extra_fmt"):
                            _ao._extra_fmt.update(ann)
                        break
            self._viewer.refresh()
            self._document.info.is_modified = True
            self._update_title()
            return

        # Label edit: replace the FreeText annotation with updated text/formatting/position
        if self._editing_label is None:
            # Fallback: the popup was likely opened for a label whose reference was lost;
            # try to locate the annotation at the popup rect's centre before giving up.
            cx = norm_rect.x() + norm_rect.width() / 2
            cy = norm_rect.y() + norm_rect.height() / 2
            found = self._form_manager.get_label_at(
                self._last_edit_page, cx, cy
            )
            if found:
                self._editing_label = found
        if self._editing_label is not None:
            label = self._editing_label
            self._editing_label = None
            text = new_text.strip() or label["text"]   # keep old text if user cleared field
            page_idx = self._last_edit_page
            # Preserve original type: "texte" blocks stay multi-line, labels stay single-line
            orig_ftype = label.get("ftype", "label")
            # Retrieve bg_white flag from the original annotation before it is replaced.
            # get_label_formatting still finds it here because add_field removes it internally.
            orig_fmt = self._form_manager.get_label_formatting(page_idx, label["name"])
            popup_bg_color = fmt.get("bg_color", "")
            # Preserve bg_white unless the user explicitly chose a background colour in the popup
            preserve_bg_white = orig_fmt.get("bg_white", False) and not popup_bg_color
            font_size = fmt.get("font_size", label.get("font_size", 12.0))
            # For OCR labels: auto-adapt box height to the new font size so the text always fits.
            final_rect = QRectF(norm_rect)
            if label.get("is_ocr"):
                _px_w2, px_h2 = self._renderer.get_page_size(page_idx, zoom=1.0)
                page_h_pt2 = px_h2 * 72.0 / 96.0
                if page_h_pt2 > 0:
                    needed_nh = (font_size * _LINE_HEIGHT_RATIO) / page_h_pt2
                    if needed_nh > final_rect.height():
                        final_rect.setHeight(needed_nh)
            self._form_manager.add_field(
                label["name"], orig_ftype, final_rect, page_idx, [text],
                font_size=font_size,
                bold=fmt.get("bold", False),
                italic=fmt.get("italic", False),
                color=fmt.get("color", "#000000"),
                underline=fmt.get("underline", False),
                letter_spacing=fmt.get("letter_spacing", 0.0),
                bg_color=popup_bg_color,
                bg_white=preserve_bg_white,
                is_ocr=label.get("is_ocr", False),
            )
            self._reload_renderer_from_doc()
            self._viewer.refresh()
            self._update_form_overlays()
            self._document.info.is_modified = True
            self._update_title()
            self._status.showMessage(
                _("Champ « {name} » modifié.").format(name=label["name"]), 3000
            )
            return

        # New text block → save directly as FreeText PDF annotation via form manager
        if getattr(self._last_word_info, "get", lambda k, v=None: v)("is_new_block", False) if isinstance(self._last_word_info, dict) else False:
            if new_text.strip():
                import uuid as _uuid
                name = f"_text_{self._last_edit_page}_{_uuid.uuid4().hex[:8]}"
                self._form_manager.add_field(
                    name, "texte", norm_rect, self._last_edit_page,
                    [new_text],
                    font_size=fmt.get("font_size", 12.0),
                    bold=fmt.get("bold", False),
                    italic=fmt.get("italic", False),
                    color=fmt.get("color", "#000000"),
                    letter_spacing=fmt.get("letter_spacing", 0.0),
                    bg_color=fmt.get("bg_color", ""),
                    no_wrap=True,
                )
                self._reload_renderer_from_doc()
                self._viewer.refresh()
                self._update_form_overlays()
                self._document.info.is_modified = True
                self._update_title()
            return

        from core.text_editor import replace_text_inplace, Method

        page_index = self._viewer.current_page
        old_text = getattr(self, "_last_word_info", {}).get("text", "")

        # Detect if the popup was moved to a different position
        _orig_nr = self._last_word_info.get("norm_rect", {}) if isinstance(self._last_word_info, dict) else {}
        # Use the full block bounding box for the cover rect when available
        # (pdfplumber's norm_rect is word-level; the block rect covers all words)
        _blk_nr = self._last_word_info.get("block_norm_rect") if isinstance(self._last_word_info, dict) else None
        _cover_nr = _blk_nr if _blk_nr else _orig_nr
        _orig_x = _orig_nr.get("x", norm_rect.x())
        _orig_y = _orig_nr.get("y", norm_rect.y())
        _orig_w = _orig_nr.get("width", norm_rect.width())
        _orig_h = _orig_nr.get("height", norm_rect.height())
        position_changed = (abs(norm_rect.x() - _orig_x) > 0.005 or
                            abs(norm_rect.y() - _orig_y) > 0.005)
        # ------------------------------------------------------------------
        # Strategy A: in-place content-stream edit (preserves embedded font)
        # Only when text actually changed AND position did NOT change.
        # ------------------------------------------------------------------
        inplace_ok = False
        if old_text and old_text != new_text and not position_changed and self._document.is_open:
            try:
                _si = self._last_word_info.get("stream_index") if isinstance(self._last_word_info, dict) else None
                _bi = self._last_word_info.get("bt_index") if isinstance(self._last_word_info, dict) else None
                ok, method = replace_text_inplace(
                    self._document.pdf, page_index, old_text, new_text,
                    stream_index=_si, bt_index=_bi,
                )
                if ok:
                    # Record the edit IMMEDIATELY — before any I/O that could throw.
                    self._edit_chain.append((page_index, old_text, new_text))

                    # Save modified PDF to a persistent temp file for the renderer.
                    try:
                        import tempfile as _tf
                        _prev = self._edit_tempfile
                        _f = _tf.NamedTemporaryFile(delete=False, suffix=".pdf")
                        tmp_path = _f.name
                        _f.close()
                        self._document.pdf.save(tmp_path)
                        self._edit_tempfile = tmp_path
                        if _prev:
                            try:
                                os.unlink(_prev)
                            except Exception:
                                pass
                        self._cache.invalidate(page_index)
                        self._renderer.load(tmp_path)
                        self._viewer.refresh()
                    except Exception as _io_exc:
                        self._status.showMessage(_("Rendu non rafraîchi : {err}").format(err=_io_exc))

                    method_label = {
                        Method.LITERAL:   "littéral",
                        Method.HEX_UTF16: "hex UTF-16",
                        Method.TJ_ARRAY:  "tableau TJ",
                    }.get(method, method)
                    self._document.info.is_modified = True
                    self._update_title()
                    self._update_actions()
                    self._status.showMessage(
                        _("Texte modifié en place ({method}). Enregistrez pour sauvegarder.").format(method=method_label)
                    )
                    inplace_ok = True
            except Exception as _exc:
                inplace_ok = False
                self._status.showMessage(_("Édition en place échouée : {err}").format(err=_exc))

        if inplace_ok:
            return

        # ------------------------------------------------------------------
        # Strategy B: injection directe dans le flux de contenu de la page.
        # Rectangle blanc sur l'original + nouveau texte au même endroit.
        # No-op si même texte ET même position.
        # ------------------------------------------------------------------
        text_to_place = new_text if new_text.strip() else old_text
        if not text_to_place:
            return

        text_changed = bool(old_text and old_text != new_text)

        # Detect formatting changes (bold, italic, font, color, size, spacing, bg)
        _wi = self._last_word_info if isinstance(self._last_word_info, dict) else {}
        # Compute block key early to compare bg_color against previously injected meta
        from core.content_injector import inject_text_block, delete_native_text_block
        import time as _time
        _block_key = f"{page_index}_{int(_orig_x * 10000)}_{int(_orig_y * 10000)}"
        _prev_block_id = self._injected_blocks.get(_block_key, "")
        _prev_meta = self._injected_meta.get(_prev_block_id, {}) if _prev_block_id else {}
        format_changed = (
            fmt.get("bold",           False)    != _wi.get("bold",       False)    or
            fmt.get("italic",         False)    != _wi.get("italic",     False)    or
            abs(fmt.get("font_size",  12.0)     -  _wi.get("font_size",  12.0)) > 0.5 or
            fmt.get("color",          "#000000")!= _wi.get("color",      "#000000") or
            fmt.get("letter_spacing", 0.0)      >  0.0                             or
            fmt.get("bg_color", "")             != _prev_meta.get("bg_color", "")  or
            fmt.get("font_family",    "")       != _wi.get("font_family", "")
        )

        if not text_changed and not position_changed and not format_changed:
            return  # rien n'a changé

        # Première injection : créer un nouveau bloc avec un id unique.
        # Injections suivantes : écraser le flux existant en place (pas de flux fantôme).
        _replace_id = ""
        if _block_key in self._injected_blocks:
            _replace_id = self._injected_blocks[_block_key]
            block_id = _replace_id  # réutiliser le même id → marqueurs stables
        else:
            block_id = f"b{int(_time.time() * 1000)}"
            self._injected_blocks[_block_key] = block_id

        # ── Page dimensions ──────────────────────────────────────────────
        import pikepdf as _pk_meta
        _page_meta = self._document.pdf.pages[page_index]
        _mb_meta = _page_meta.get("/MediaBox", _pk_meta.Array([0, 0, 595, 842]))
        _pw_meta = float(_mb_meta[2]) - float(_mb_meta[0])
        _ph_meta = float(_mb_meta[3]) - float(_mb_meta[1])

        # ── Cover rect ───────────────────────────────────────────────────
        # _cover_nr.y is at the BASELINE (PDF text origin), not the top of
        # characters.  Ascenders (capitals, 'd', 'f' …) extend above the
        # baseline by ~0.75 × font_size.  We therefore push the cover rect
        # upward by that amount so the whole glyph is hidden.
        _cx = _cover_nr.get("x", _orig_x)
        _cy = _cover_nr.get("y", _orig_y)
        _cw = _cover_nr.get("width", _orig_w)
        _ch = _cover_nr.get("height", _orig_h)

        # Font size of the original block (not the new requested size)
        _orig_fs = _wi.get("block_font_size") or _wi.get("font_size", 12.0)
        _orig_fs_norm = _orig_fs / _ph_meta          # normalised ascender unit

        _margin_y_top = max(_orig_fs_norm * 0.85, _ch * 0.1, 0.003)   # covers ascenders
        _margin_y_bot = max(_orig_fs_norm * 0.25, 0.002)               # covers descenders
        _margin_x     = 0.005

        # ── Text width: large enough to avoid wrapping the new text ──────
        _font_sz = fmt.get("font_size", 12.0)
        _est_nw = len(text_to_place) * _font_sz * 0.62 / _pw_meta + 0.02
        _text_nw = max(norm_rect.width(), _est_nw)
        _text_nw = min(_text_nw, 1.0 - norm_rect.x())

        ok = inject_text_block(
            self._document.pdf, page_index, block_id,
            cover_nx=max(0.0, _cx - _margin_x),
            cover_ny=max(0.0, _cy - _margin_y_top),
            cover_nw=_cw + 2 * _margin_x,
            cover_nh=_ch + _margin_y_top + _margin_y_bot,
            text_nx=norm_rect.x(),
            text_ny=norm_rect.y(),
            text_nw=_text_nw,
            text_nh=norm_rect.height(),
            text=text_to_place,
            font_size=_font_sz,
            bold=fmt.get("bold", False),
            italic=fmt.get("italic", False),
            color=fmt.get("color", "#000000"),
            letter_spacing=fmt.get("letter_spacing", 0.0),
            font_family=fmt.get("font_family", "Helvetica"),
            bg_color=fmt.get("bg_color", ""),
            replace_block_id=_replace_id,
        )

        self._injected_meta[block_id] = {
            "text": text_to_place,
            "font_size": _font_sz,
            "bold": fmt.get("bold", False),
            "italic": fmt.get("italic", False),
            "color": fmt.get("color", "#000000"),
            "font_family": fmt.get("font_family", "Helvetica"),
            "bg_color": fmt.get("bg_color", ""),
            "letter_spacing": fmt.get("letter_spacing", 0.0),
            "cover_nx": max(0.0, _cx - _margin_x),
            "cover_ny": max(0.0, _cy - _margin_y_top),
            "cover_nw": _cw + 2 * _margin_x,
            "cover_nh": _ch + _margin_y_top + _margin_y_bot,
            "text_nw": _text_nw,
        }

        if text_changed:
            self._edit_chain.append((page_index, old_text, new_text))

        if ok:
            # Suppression automatique du texte original du stream (Strategy B ajoute
            # un rectangle blanc, mais le texte source reste sinon dans le stream 0).
            _native_blk = _wi.get("native_block")
            if _native_blk is not None:
                delete_native_text_block(self._document.pdf, page_index, _native_blk)

            self._reload_renderer_from_doc()
            self._viewer.refresh()
            self._document.info.is_modified = True
            self._update_title()
            self._update_actions()
            self._status.showMessage(_("Texte modifié. Enregistrez pour sauvegarder."))

    # ------------------------------------------------------------------
    # Text block move (move_block tool)
    # ------------------------------------------------------------------

    def _on_block_pick_requested(self, norm_x: float, norm_y: float) -> None:
        """Find the text block at the click position and set the drag ghost on the viewer."""
        if not self._document.is_open:
            return
        from core.block_detector import get_block_at, get_injected_block_at
        from PySide6.QtCore import QRectF as _QRectF
        import pikepdf as _pikepdf
        page_index = self._viewer.current_page

        # Check injected blocks first (they are rendered on top)
        inj = get_injected_block_at(self._document.pdf, page_index, norm_x, norm_y)
        if inj is not None:
            ghost = _QRectF(inj.norm_x, inj.norm_y, inj.norm_w, inj.norm_h)
            self._moving_block = None
            self._moving_injected = inj
            self._moving_block_page = page_index
            self._last_deletable = {"type": "block", "page_idx": page_index, "block_id": inj.block_id}
            self._viewer.set_block_ghost(ghost)
            return

        block = get_block_at(self._document.pdf, page_index, norm_x, norm_y)
        if block is None:
            self._last_deletable = None  # click on empty area → clear selection
            self._debug_move_log(f"PICK  ({norm_x:.4f}, {norm_y:.4f}) → aucun bloc")
            return
        page = self._document.pdf.pages[page_index]
        mb = page.get("/MediaBox", _pikepdf.Array([0, 0, 595, 842]))
        pw = float(mb[2]) - float(mb[0])
        ph = float(mb[3]) - float(mb[1])
        nr = block.norm_rect(pw, ph)
        ghost = _QRectF(nr["x"], nr["y"], nr["width"], nr["height"])
        self._moving_block = block
        self._moving_injected = None
        self._moving_block_page = page_index
        self._viewer.set_block_ghost(ghost)
        self._debug_move_log(
            f"PICK  clic=({norm_x:.4f},{norm_y:.4f})  "
            f"bloc_nr=({nr['x']:.4f},{nr['y']:.4f},{nr['width']:.4f},{nr['height']:.4f})  "
            f"baseline_pdf=({block.x0:.1f},{block.y1:.1f})  "
            f"« {block.text[:30].replace(chr(10),' ')} »"
        )

    def _on_block_move_requested(
        self,
        orig_x: float, orig_y: float,
        new_norm_x: float, new_norm_y: float,
        new_norm_w: float = 0.0,
    ) -> None:
        """Move/resize the previously picked block to the new position (undoable)."""
        # Ignore si pas de déplacement réel (simple clic sans drag) — évite le rect blanc parasite
        _moved = abs(new_norm_x - orig_x) > 0.003 or abs(new_norm_y - orig_y) > 0.003
        _resized = new_norm_w > 0.01
        if not _moved and not _resized:
            return

        page_index = getattr(self, "_moving_block_page", self._viewer.current_page)
        inj = getattr(self, "_moving_injected", None)
        block = getattr(self, "_moving_block", None)
        # Keep _moving_block/_moving_injected so the user can keep dragging the same block

        # --- Move an injected block (re-inject at new position) ---
        if inj is not None:
            meta = self._injected_meta.get(inj.block_id, {})
            text = meta.get("text", inj.text)
            dx = new_norm_x - inj.norm_x
            dy = new_norm_y - inj.norm_y
            new_cover_nx = max(0.0, meta.get("cover_nx", inj.norm_x) + dx)
            new_cover_ny = max(0.0, meta.get("cover_ny", inj.norm_y) + dy)
            cover_nw = meta.get("cover_nw", inj.norm_w)
            cover_nh = meta.get("cover_nh", inj.norm_h)

            # Use ghost width if user resized (new_norm_w > 0 and differs from stored)
            user_resized = new_norm_w > 0.01 and abs(new_norm_w - (meta.get("text_nw", 0) or inj.norm_w)) > 0.01
            if user_resized:
                text_nw = new_norm_w
            else:
                # Ensure text_nw is wide enough to prevent wrapping
                stored_nw = meta.get("text_nw", 0.0)
                import pikepdf as _pk_mv
                _page_mv = self._document.pdf.pages[page_index]
                _mb_mv = _page_mv.get("/MediaBox", _pk_mv.Array([0, 0, 595, 842]))
                _pw_mv = float(_mb_mv[2]) - float(_mb_mv[0])
                fs = meta.get("font_size", inj.font_size)
                est_nw = len(text) * fs * 0.62 / _pw_mv + 0.02
                text_nw = max(stored_nw, est_nw, inj.norm_w)
                text_nw = min(text_nw, 1.0 - new_norm_x)

            from core.content_injector import inject_text_block
            from PySide6.QtCore import QRectF as _QRectF2
            ok = inject_text_block(
                self._document.pdf, page_index, inj.block_id,
                cover_nx=new_cover_nx,
                cover_ny=new_cover_ny,
                cover_nw=cover_nw,
                cover_nh=cover_nh,
                text_nx=new_norm_x,
                text_ny=new_norm_y,
                text_nw=text_nw,
                text_nh=cover_nh,
                text=text,
                font_size=meta.get("font_size", inj.font_size),
                bold=meta.get("bold", False),
                italic=meta.get("italic", False),
                color=meta.get("color", "#000000"),
                letter_spacing=meta.get("letter_spacing", 0.0),
                font_family=meta.get("font_family", "Helvetica"),
                bg_color=meta.get("bg_color", ""),
                replace_block_id=inj.block_id,
            )
            if ok:
                # Update stored metadata with new position
                self._injected_meta[inj.block_id] = dict(meta)
                self._injected_meta[inj.block_id].update({
                    "cover_nx": new_cover_nx,
                    "cover_ny": new_cover_ny,
                    "text_nw": text_nw,
                })
                # Update inj reference to reflect new position for next drag
                inj.norm_x = new_norm_x
                inj.norm_y = new_norm_y
                self._reload_renderer_from_doc()
                self._cache.invalidate(page_index)
                self._viewer.refresh()
                # Keep ghost at the new position (persistent selection)
                ghost = _QRectF2(new_norm_x, new_norm_y, text_nw, cover_nh)
                self._viewer.set_block_ghost(ghost, start_dragging=False)
                self._document.info.is_modified = True
                self._update_title()
                self._update_actions()
                self._status.showMessage(_("Bloc déplacé. Enregistrez pour sauvegarder."))
            return

        # --- Move a native text block ---
        if block is None:
            return

        cmd = MoveTextBlockCommand(
            pdf=self._document.pdf,
            page_index=page_index,
            block=block,
            new_norm_x=new_norm_x,
            new_norm_y=new_norm_y,
            reload_fn=self._reload_renderer_from_doc,
            cache=self._cache,
            viewer=self._viewer,
        )
        # Log debug avant l'exécution (coordonnées du bloc AVANT déplacement)
        import pikepdf as _pk_mv2
        _page_mv2 = self._document.pdf.pages[page_index]
        _mb_mv2 = _page_mv2.get("/MediaBox", _pk_mv2.Array([0, 0, 595, 842]))
        _pw_mv2 = float(_mb_mv2[2]) - float(_mb_mv2[0])
        _ph_mv2 = float(_mb_mv2[3]) - float(_mb_mv2[1])
        _dx_pdf = new_norm_x * _pw_mv2 - block.x0
        _dy_pdf = (1.0 - new_norm_y) * _ph_mv2 - block.y1
        self._debug_move_log(
            f"MOVE  orig=({orig_x:.4f},{orig_y:.4f})  "
            f"target=({new_norm_x:.4f},{new_norm_y:.4f})  "
            f"bloc_pdf_x0={block.x0:.1f} y1={block.y1:.1f}  "
            f"dx={_dx_pdf:.2f}pt dy={_dy_pdf:.2f}pt"
        )

        self._history.push(cmd)

        # Mettre à jour le ghost à la nouvelle position (même dimensions, nouveau coin)
        _nr_mv2 = block.norm_rect(_pw_mv2, _ph_mv2)
        from PySide6.QtCore import QRectF as _QRectF3
        _new_ghost = _QRectF3(new_norm_x, new_norm_y, _nr_mv2["width"], _nr_mv2["height"])
        self._viewer.set_block_ghost(_new_ghost, start_dragging=False)

        # Mettre à jour les coordonnées du bloc en mémoire pour éviter le drift
        # (les items reflètent maintenant la position dans le stream modifié)
        for _line in block.lines:
            for _item in _line.items:
                _item.x += _dx_pdf
                _item.y += _dy_pdf

        self._debug_move_log(
            f"      → nouveau bloc_pdf_x0={block.x0:.1f} y1={block.y1:.1f}  "
            f"ghost=({new_norm_x:.4f},{new_norm_y:.4f})"
        )

        self._moving_block = block  # garder la référence avec coordonnées à jour
        self._document.info.is_modified = True
        self._update_title()
        self._update_actions()
        self._status.showMessage(_("Bloc déplacé. Enregistrez pour sauvegarder."))

    # ------------------------------------------------------------------
    # Debug — move window
    # ------------------------------------------------------------------

    def _debug_move_log(self, msg: str) -> None:
        """Append a line to the debug move dock (creates it on first call)."""
        if self._debug_move_dock is None:
            return
        from PySide6.QtWidgets import QTextEdit as _QTE
        te = self._debug_move_dock.widget()
        if isinstance(te, _QTE):
            te.append(msg)

    def toggle_debug_move(self) -> None:
        """Show / hide the floating debug window for block moves."""
        from PySide6.QtWidgets import QDockWidget, QTextEdit as _QTE
        from PySide6.QtCore import Qt as _Qt
        if self._debug_move_dock is not None:
            self._debug_move_dock.setVisible(not self._debug_move_dock.isVisible())
            return
        dock = QDockWidget("Debug — déplacement blocs", self)
        dock.setAllowedAreas(_Qt.DockWidgetArea.NoDockWidgetArea)
        dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable |
            QDockWidget.DockWidgetFeature.DockWidgetFloatable |
            QDockWidget.DockWidgetFeature.DockWidgetClosable
        )
        te = _QTE()
        te.setReadOnly(True)
        te.setLineWrapMode(_QTE.LineWrapMode.NoWrap)
        te.setStyleSheet("font-family: monospace; font-size: 11px;")
        dock.setWidget(te)
        dock.setFloating(True)
        dock.resize(640, 340)
        dock.show()
        self._debug_move_dock = dock

    # ------------------------------------------------------------------
    # Undo / Redo
    # ------------------------------------------------------------------

    def undo(self) -> None:
        cmd = self._history.undo()
        if cmd:
            self._status.showMessage(_("Annulé : {desc}").format(desc=cmd.description))
            self._update_actions()

    def redo(self) -> None:
        cmd = self._history.redo()
        if cmd:
            self._status.showMessage(_("Rétabli : {desc}").format(desc=cmd.description))
            self._update_actions()

    # ------------------------------------------------------------------
    # Panel action dispatcher
    # ------------------------------------------------------------------

    def _on_panel_action(self, action_id: str) -> None:
        """Dispatch actions triggered from the left PDF-tools panel."""
        _map = {
            "insert_image": self._insert_image_from_menu,
            "insert_text":  lambda: self._on_form_design_mode(True),
            "move_block":   self._activate_move_block_tool,
            "organize":     self._organize_pages,
            "split":        self._split_pdf,
            "delete_page":  self._delete_current_page,
            "extract_text": self._extract_text,
            "extract_img":  self._extract_images,
            "metadata":     self._edit_metadata,
            "hf":           self._add_header_footer,
            "watermark":    self._add_watermark,
            "stamp_text":   self._add_stamp,
            "stamp_image":  self._add_image_stamp,
            "compress":     self._compress_pdf,
            "protect":      self._protect_pdf,
            "unlock":       self._unlock_pdf,
            "sign":         self._sign_document,
            "verify_sigs":  self._verify_signatures,
            "rotate_cw":    lambda: self._rotate_current(90),
            "rotate_ccw":   lambda: self._rotate_current(-90),
            "search":       self._open_search,
            "ocr":          self._open_ocr,
        }
        handler = _map.get(action_id)
        if handler:
            handler()

    # ------------------------------------------------------------------
    # PDF Tools
    # ------------------------------------------------------------------

    def open_combine(self, paths: list) -> None:
        """Open the Organize dialog pre-loaded with files from right-click multi-select."""
        self._organize_pages(initial_files=paths)

    def _organize_pages(self, initial_files: list | None = None) -> None:
        from ui.dialogs.organize_dialog import OrganizeDialog
        from core.tools import PDFTools

        has_doc = self._document.is_open
        renderer   = self._renderer if has_doc else None
        page_count = self._document.page_count if has_doc else 0

        dlg = OrganizeDialog(renderer, page_count, self, initial_files=initial_files)
        if dlg.exec() != OrganizeDialog.DialogCode.Accepted:
            return

        try:
            if has_doc:
                # Normal mode — modify current document in-place (undoable)
                page_specs = dlg.page_specs

                def _do_reorder():
                    PDFTools.reorder_pages(self._document.pdf, page_specs)

                def _refresh_reorder():
                    self._reload_renderer_from_doc()
                    self._viewer.display_page(0)
                    self._sidebar.load_thumbnails(self._renderer)
                    self._document.info.is_modified = True
                    self._update_title()

                cmd = PdfStructureCommand(
                    self._document.pdf, _do_reorder,
                    "Réorganiser les pages",
                    _refresh_reorder,
                )
                self._history.push(cmd)
                self._update_actions()
                self._status.showMessage(
                    _("Pages réorganisées — pensez à enregistrer (Ctrl+S)."), 5000
                )
            else:
                # No document open — build a brand-new PDF from the assembled pages
                if not dlg.page_specs:
                    return
                path, _filt = QFileDialog.getSaveFileName(
                    self, _("Enregistrer le nouveau PDF"), "", _("PDF (*.pdf)")
                )
                if not path:
                    return
                if not path.lower().endswith(".pdf"):
                    path += ".pdf"
                import pikepdf as _pk
                new_pdf = _pk.Pdf.new()
                PDFTools.reorder_pages(new_pdf, dlg.page_specs)
                new_pdf.save(path)
                new_pdf.close()
                self.open_file(path)
                self._status.showMessage(
                    _("Nouveau PDF créé et ouvert : {name}").format(
                        name=os.path.basename(path)
                    ), 5000
                )
        except Exception as e:
            QMessageBox.critical(self, _("Erreur"), str(e))

    def _split_pdf(self) -> None:
        if not self._document.is_open:
            return
        from ui.dialogs.split_dialog import SplitDialog
        dlg = SplitDialog(self._document.path, self._document.page_count, self)
        dlg.exec()

    def _extract_text(self) -> None:
        if not self._document.is_open:
            return
        from core.tools import PDFTools
        from PySide6.QtWidgets import (
            QDialog, QVBoxLayout, QHBoxLayout, QLabel,
            QSpinBox, QRadioButton, QButtonGroup, QDialogButtonBox,
        )

        total = self._document.page_count
        current = self._viewer.current_page + 1  # 1-based for display

        # ── Page-range dialog ──────────────────────────────────────────────
        dlg = QDialog(self)
        dlg.setWindowTitle(_("Extraire le texte"))
        dlg.setMinimumWidth(320)
        lay = QVBoxLayout(dlg)
        lay.setSpacing(10)

        lay.addWidget(QLabel(f"<b>{_('Pages à extraire')}</b> ({total} {_('page(s) au total')})"))

        # Adapt colors to current theme
        is_dark = self._config.get("theme", "dark") == "dark"
        rb_style = (
            "QRadioButton { padding: 6px 8px; border-radius: 4px; font-size: 13px; }"
            "QRadioButton::indicator { width: 14px; height: 14px; }"
        ) + (
            # Dark theme
            "QRadioButton { color: #e0e0e0; }"
            "QRadioButton:hover { background: #3a3a4e; }"
            "QRadioButton:checked { background: #2a4a7a; color: #ffffff; font-weight: bold; }"
            "QRadioButton::indicator:unchecked { border: 2px solid #888; border-radius: 7px; background: #2a2a3a; }"
            "QRadioButton::indicator:checked  { border: 2px solid #4a90d9; border-radius: 7px; background: #4a90d9; }"
            if is_dark else
            # Light theme
            "QRadioButton { color: #1a1a1a; }"
            "QRadioButton:hover { background: #dde8f8; }"
            "QRadioButton:checked { background: #c5d8f5; color: #0a2a5a; font-weight: bold; }"
            "QRadioButton::indicator:unchecked { border: 2px solid #aaa; border-radius: 7px; background: #f5f5f5; }"
            "QRadioButton::indicator:checked  { border: 2px solid #2a6abf; border-radius: 7px; background: #2a6abf; }"
        )

        # Radio: all pages
        rb_all = QRadioButton(_("Toutes les pages"))
        rb_all.setChecked(True)

        # Radio: current page only
        rb_cur = QRadioButton(_("Page courante ({n})").format(n=current))

        # Radio: custom range
        rb_range = QRadioButton(_("Intervalle :"))

        grp = QButtonGroup(dlg)
        for rb in (rb_all, rb_cur, rb_range):
            grp.addButton(rb)
            rb.setStyleSheet(rb_style)
            lay.addWidget(rb)

        # Spinboxes for range
        row = QHBoxLayout()
        lbl_from = QLabel(_("De la page"))
        spin_from = QSpinBox()
        spin_from.setRange(1, total)
        spin_from.setValue(1)
        lbl_to = QLabel(_("à"))
        spin_to = QSpinBox()
        spin_to.setRange(1, total)
        spin_to.setValue(total)
        for w in (lbl_from, spin_from, lbl_to, spin_to):
            row.addWidget(w)
        row.addStretch()
        lay.addLayout(row)

        # Enable spinboxes only when range radio is selected
        def _toggle_spins():
            enabled = rb_range.isChecked()
            for w in (spin_from, spin_to, lbl_from, lbl_to):
                w.setEnabled(enabled)
        _toggle_spins()
        rb_all.toggled.connect(_toggle_spins)
        rb_cur.toggled.connect(_toggle_spins)
        rb_range.toggled.connect(_toggle_spins)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dlg.accept)
        buttons.rejected.connect(dlg.reject)
        lay.addWidget(buttons)

        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        # Resolve page range (0-based)
        if rb_all.isChecked():
            page_range = None
        elif rb_cur.isChecked():
            p = self._viewer.current_page
            page_range = (p, p)
        else:
            p1 = spin_from.value() - 1
            p2 = max(spin_to.value() - 1, p1)
            page_range = (p1, p2)

        try:
            text = PDFTools.extract_text(self._document.path, page_range=page_range)
            if not text.strip():
                QMessageBox.information(self, _("Extraction"), _("Aucun texte trouvé dans la sélection."))
                return
            path, _filt = QFileDialog.getSaveFileName(
                self, _("Exporter le texte"), "", _("Texte (*.txt)")
            )
            if not path:
                return
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)

            # ── Résumé de l'extraction ────────────────────────────────────
            import os
            n_chars = len(text)
            n_words = len(text.split())
            n_lines = text.count("\n") + 1
            file_kb = round(os.path.getsize(path) / 1024, 1)

            if page_range is None:
                pages_desc = _("Toutes les pages ({n})").format(n=total)
            elif page_range[0] == page_range[1]:
                pages_desc = _("Page {n}").format(n=page_range[0] + 1)
            else:
                pages_desc = _("Pages {a} à {b}").format(
                    a=page_range[0] + 1, b=page_range[1] + 1
                )

            QMessageBox.information(
                self,
                _("Extraction réussie ✅"),
                (
                    f"<b>{_('Extraction terminée avec succès !')}</b><br><br>"
                    f"📄 <b>{_('Pages extraites :')}</b> {pages_desc}<br>"
                    f"🔤 <b>{_('Caractères :')}</b> {n_chars:,}<br>"
                    f"📝 <b>{_('Mots :')}</b> {n_words:,}<br>"
                    f"↵ <b>{_('Lignes :')}</b> {n_lines:,}<br>"
                    f"💾 <b>{_('Fichier :')}</b> {os.path.basename(path)} ({file_kb} Ko)"
                ),
            )
            self._status.showMessage(_("Texte exporté : {path}").format(path=path))
        except Exception as e:
            QMessageBox.critical(self, _("Erreur"), str(e))

    def _extract_images(self) -> None:
        if not self._document.is_open:
            return
        from core.tools import PDFTools
        out_dir = QFileDialog.getExistingDirectory(self, _("Dossier de sortie"))
        if not out_dir:
            return
        try:
            paths = PDFTools.extract_images(self._document.path, out_dir)
            QMessageBox.information(self, _("Succès"), _("{n} image(s) extraite(s).").format(n=len(paths)))
        except Exception as e:
            QMessageBox.critical(self, _("Erreur"), str(e))

    def _add_header_footer(self) -> None:
        if not self._document.is_open:
            return
        from ui.dialogs.header_footer_dialog import HeaderFooterDialog
        from core.tools import PDFTools
        initial = getattr(self, "_hf_settings", None)
        dlg = HeaderFooterDialog(self._document.page_count, self, initial=initial)
        if dlg.exec() != HeaderFooterDialog.DialogCode.Accepted:
            return
        try:
            if not any(dlg.header + dlg.footer):
                # Empty fields → remove existing HF (undoable)
                def _do_remove():
                    PDFTools._remove_hf_streams(self._document.pdf)
                    self._hf_settings = None
                cmd = PageStreamsCommand(
                    self._document.pdf, _do_remove,
                    "Supprimer en-têtes/pieds de page",
                    self._refresh_after_pdf_change,
                )
                self._history.push(cmd)
                self._update_actions()
                self._status.showMessage(_("En-têtes/pieds de page supprimés."), 4000)
                return
            # Capture dialog values now (closure)
            header, footer = dlg.header, dlg.footer
            font_size, color = dlg.font_size, dlg.color
            margin_mm, skip_first = dlg.margin_mm, dlg.skip_first

            def _do_add():
                PDFTools.add_header_footer(
                    self._document.pdf,
                    header=header, footer=footer,
                    font_size=font_size, color=color,
                    margin_mm=margin_mm, skip_first=skip_first,
                )
                self._hf_settings = {
                    "header": header, "footer": footer,
                    "font_size": font_size, "color": color,
                    "margin_mm": margin_mm, "skip_first": skip_first,
                }
            cmd = PageStreamsCommand(
                self._document.pdf, _do_add,
                "En-têtes et pieds de page",
                self._refresh_after_pdf_change,
            )
            self._history.push(cmd)
            self._update_actions()
            self._status.showMessage(
                _("En-têtes/pieds de page ajoutés — pensez à enregistrer (Ctrl+S)."), 5000
            )
        except Exception as e:
            QMessageBox.critical(self, _("Erreur"), str(e))

    def _add_watermark(self) -> None:
        if not self._document.is_open:
            return
        from ui.dialogs.watermark_dialog import WatermarkDialog
        from core.tools import PDFTools
        dlg = WatermarkDialog(self)
        if dlg.exec() != WatermarkDialog.DialogCode.Accepted:
            return
        try:
            text, opacity, font_size, color = (
                dlg.watermark_text, dlg.opacity, dlg.font_size, dlg.color
            )

            def _do():
                PDFTools.add_watermark(
                    self._document.pdf,
                    text=text, opacity=opacity,
                    font_size=font_size, color=color,
                )
            cmd = PageStreamsCommand(
                self._document.pdf, _do,
                f"Filigrane « {text} »",
                self._refresh_after_pdf_change,
            )
            self._history.push(cmd)
            self._update_actions()
            self._status.showMessage(
                _("Filigrane ajouté sur toutes les pages — pensez à enregistrer (Ctrl+S)."), 5000
            )
        except Exception as e:
            QMessageBox.critical(self, _("Erreur"), str(e))

    def _add_stamp(self) -> None:
        if not self._document.is_open:
            return
        from ui.dialogs.stamp_dialog import StampDialog
        from core.tools import PDFTools
        dlg = StampDialog(self)
        if dlg.exec() != StampDialog.DialogCode.Accepted:
            return
        try:
            stamp_text, color, position, pages, opacity, rotation = (
                dlg.stamp_text, dlg.color, dlg.position,
                dlg.pages, dlg.opacity, dlg.rotation,
            )
            n = _("toutes les pages") if pages == "all" else (
                _("la première page") if pages == "first" else _("la dernière page")
            )

            def _do():
                PDFTools.add_stamp(
                    self._document.pdf,
                    text=stamp_text, color=color, position=position,
                    pages=pages, opacity=opacity, rotation=rotation,
                )
            cmd = PageStreamsCommand(
                self._document.pdf, _do,
                f"Tampon « {stamp_text} »",
                self._refresh_after_pdf_change,
            )
            self._history.push(cmd)
            self._update_actions()
            self._status.showMessage(
                _("Tampon « {t} » ajouté sur {n} — pensez à enregistrer (Ctrl+S).").format(
                    t=stamp_text, n=n
                ), 5000
            )
        except Exception as e:
            QMessageBox.critical(self, _("Erreur"), str(e))

    def _add_image_stamp(self) -> None:
        if not self._document.is_open:
            return
        from ui.dialogs.image_stamp_dialog import ImageStampDialog
        from core.tools import PDFTools
        dlg = ImageStampDialog(self)
        if dlg.exec() != ImageStampDialog.DialogCode.Accepted:
            return
        if not dlg.selected_image_path:
            return
        try:
            image_path, position, pages, scale_pct, opacity = (
                dlg.selected_image_path, dlg.position,
                dlg.pages, dlg.scale_pct, dlg.opacity,
            )
            n = _("toutes les pages") if pages == "all" else (
                _("la première page") if pages == "first" else _("la dernière page")
            )

            def _do():
                PDFTools.add_image_stamp(
                    self._document.pdf,
                    image_path=image_path, position=position,
                    pages=pages, scale_pct=scale_pct, opacity=opacity,
                )
            cmd = PageStreamsCommand(
                self._document.pdf, _do,
                "Tampon image",
                self._refresh_after_pdf_change,
            )
            self._history.push(cmd)
            self._update_actions()
            self._status.showMessage(
                _("Tampon image appliqué sur {n} — pensez à enregistrer (Ctrl+S).").format(n=n),
                5000
            )
        except Exception as e:
            QMessageBox.critical(self, _("Erreur"), str(e))

    def _edit_metadata(self) -> None:
        if not self._document.is_open:
            return
        from ui.dialogs.metadata_dialog import MetadataDialog
        from core.tools import PDFTools
        old_meta = PDFTools.get_metadata(self._document.pdf)
        dlg = MetadataDialog(old_meta, self)
        if dlg.exec() != MetadataDialog.DialogCode.Accepted:
            return
        new_meta = dlg.metadata

        def _apply(meta):
            PDFTools.set_metadata(self._document.pdf, meta)
            self._document.info.is_modified = True
            self._update_title()

        cmd = MetadataCommand(
            self._document.pdf, old_meta, new_meta,
            _apply,
            lambda: self._status.showMessage(
                _("Métadonnées mises à jour — pensez à enregistrer (Ctrl+S)."), 4000
            ),
        )
        self._history.push(cmd)
        self._update_actions()

    def _compress_pdf(self) -> None:
        if not self._document.is_open:
            return
        from core.tools import PDFTools
        try:
            saving_holder = [0]

            def _do():
                saving_holder[0] = PDFTools.compress(self._document.pdf)

            cmd = PageStreamsCommand(
                self._document.pdf, _do,
                "Compresser le PDF",
                self._refresh_after_pdf_change,
            )
            self._history.push(cmd)
            self._update_actions()
            if saving_holder[0] > 0:
                self._status.showMessage(
                    _("Compression effectuée — gain estimé : {kb} Ko. Enregistrez pour finaliser (Ctrl+S).").format(
                        kb=round(saving_holder[0] / 1024, 1)), 6000)
            else:
                self._status.showMessage(
                    _("Le document est déjà optimal — aucun gain de compression possible."), 4000)
        except Exception as e:
            QMessageBox.critical(self, _("Erreur"), str(e))

    def _protect_pdf(self) -> None:
        if not self._document.is_open:
            return
        from core.tools import PDFTools
        pw, ok = QInputDialog.getText(self, _("Protection"), _("Mot de passe :"),
                                      QLineEdit.EchoMode.Password, "")
        if not ok or not pw:
            return
        default_dir = os.path.dirname(self._document.path) if self._document.path else ""
        out, _filt = QFileDialog.getSaveFileName(self, _("Enregistrer sous…"), default_dir, _("PDF (*.pdf)"))
        if out:
            try:
                PDFTools.protect(self._document.path, out, pw)
                self._status.showMessage(_("PDF protégé enregistré."))
            except Exception as e:
                QMessageBox.critical(self, _("Erreur"), str(e))

    def _unlock_pdf(self) -> None:
        if not self._document.is_open:
            return
        from core.tools import PDFTools
        pw, ok = QInputDialog.getText(self, _("Déverrouillage"), _("Mot de passe :"),
                                      QLineEdit.EchoMode.Password, "")
        if not ok:
            return
        default_dir = os.path.dirname(self._document.path) if self._document.path else ""
        out, _filt = QFileDialog.getSaveFileName(self, _("Enregistrer sous…"), default_dir, _("PDF (*.pdf)"))
        if out:
            try:
                PDFTools.unlock(self._document.path, out, pw)
                self._status.showMessage(_("PDF déprotégé enregistré."))
            except Exception as e:
                QMessageBox.critical(self, _("Erreur"), str(e))

    def _ensure_owner_access(self) -> bool:
        """
        Returns True if the document can be modified.
        If encrypted and not yet owner-unlocked, asks for the password.
        """
        if not self._document.is_open:
            return False
        if not self._document.needs_owner_password:
            return True
        pw, ok = QInputDialog.getText(
            self, _("Mot de passe requis"),
            _("Ce document est protégé. Entrez le mot de passe pour le modifier :"),
            QLineEdit.EchoMode.Password, "",
        )
        if not ok or not pw:
            return False
        if self._document.try_unlock_as_owner(pw):
            self._status.showMessage(_("Document déverrouillé — modifications autorisées."))
            return True
        QMessageBox.warning(self, _("Erreur"), _("Mot de passe incorrect."))
        return False

    def _refresh_after_pdf_change(self) -> None:
        """Standard post-operation refresh used by snapshot commands."""
        self._reload_renderer_from_doc()
        self._viewer.refresh()
        self._document.info.is_modified = True
        self._update_title()

    def _reload_renderer_from_doc(self) -> None:
        """Save current pikepdf state to a temp file and reload the renderer."""
        import tempfile as _tf
        _f = _tf.NamedTemporaryFile(delete=False, suffix=".pdf")
        tmp_path = _f.name
        _f.close()
        self._document.pdf.save(tmp_path)
        _prev = self._edit_tempfile
        self._edit_tempfile = tmp_path
        self._cache.invalidate(self._viewer.current_page)
        self._renderer.load(tmp_path)
        if _prev:
            try:
                os.unlink(_prev)
            except Exception:
                pass

    def _rotate_current(self, degrees: int) -> None:
        if not self._document.is_open:
            return
        if not self._ensure_owner_access():
            return
        cmd = PageRotateCommand(
            self._document, self._renderer, self._viewer,
            self._viewer.current_page, degrees, self._cache,
            reload_fn=self._reload_renderer_from_doc,
        )
        self._history.push(cmd)
        self._update_actions()

    # ------------------------------------------------------------------
    # Signature
    # ------------------------------------------------------------------

    def _sign_document(self) -> None:
        if not self._document.is_open:
            return
        from ui.dialogs.sign_dialog import SignDialog
        dlg = SignDialog(self._document.path, self._document.page_count, self)
        dlg.exec()

    def _verify_signatures(self) -> None:
        if not self._document.is_open:
            return
        from core.signature import SignatureEngine
        engine = SignatureEngine()
        results = engine.verify(self._document.path)
        if not results:
            QMessageBox.information(self, _("Signatures"), _("Aucune signature trouvée."))
            return
        text = "\n\n".join(
            "\n".join(f"{k}: {v}" for k, v in r.items())
            for r in results
        )
        QMessageBox.information(self, _("Signatures"), text)

    # ------------------------------------------------------------------
    # View
    # ------------------------------------------------------------------

    def _toggle_sidebar(self) -> None:
        self._sidebar_dock.setVisible(not self._sidebar_dock.isVisible())

    def _toggle_right_panel(self) -> None:
        self._right_dock.setVisible(not self._right_dock.isVisible())

    def _switch_theme(self, theme: str) -> None:
        self._config.set("theme", theme)
        theme_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "assets", "themes", f"{theme}.qss",
        )
        if os.path.exists(theme_path):
            with open(theme_path, "r", encoding="utf-8") as f:
                QApplication.instance().setStyleSheet(f.read())

    # ------------------------------------------------------------------
    # OCR
    # ------------------------------------------------------------------

    def _provide_image_to_ocr(self) -> None:
        # Render at 3× zoom (~288 dpi) for much better Tesseract accuracy.
        img = self._viewer._renderer.render_page(
            self._viewer.current_page, zoom=3.0
        )
        if img:
            self._ocr_panel.set_image(img)
            self._ocr_panel._run_ocr()

    def _on_ocr_close_requested(self) -> None:
        """Fermer le panneau OCR — propose d'enregistrer si le document est modifié."""
        if self._document.is_open and self._document.info.is_modified:
            box = QMessageBox(self)
            box.setIcon(QMessageBox.Icon.Question)
            box.setWindowTitle(_("Modifications non enregistrées"))
            box.setText(_("Des modifications ont été apportées. Enregistrer avant de fermer ?"))
            btn_save    = box.addButton(_("Enregistrer"),        QMessageBox.ButtonRole.AcceptRole)
            btn_discard = box.addButton(_("Ne pas enregistrer"), QMessageBox.ButtonRole.DestructiveRole)
            box.addButton(_("Annuler"),                          QMessageBox.ButtonRole.RejectRole)
            box.setDefaultButton(btn_save)
            box.exec()
            clicked = box.clickedButton()
            if clicked == btn_save:
                self.save_file()
            elif clicked != btn_discard:
                return   # Annuler → ne pas fermer
        self._ocr_dock.hide()

    def _on_ocr_lines_ready(self, lines: list, img_w: int, img_h: int) -> None:
        """Store OCR lines and refresh the Qt preview overlay."""
        self._pending_ocr_lines = lines
        self._pending_ocr_img_w = img_w
        self._pending_ocr_img_h = img_h
        self._ocr_overlay_widths.clear()   # reset any previous resize overrides
        self._update_ocr_viewer_preview()

    def _on_ocr_preview_settings_changed(self, opacity: float, bg_white: bool) -> None:
        """Slider or checkbox changed — update the Qt overlay in real-time."""
        self._update_ocr_viewer_preview(opacity=opacity, bg_white=bg_white)

    def _update_ocr_viewer_preview(
        self,
        opacity: float | None = None,
        bg_white: bool | None = None,
    ) -> None:
        """Redraw the OCR overlay on the viewer with current settings."""
        if not self._pending_ocr_lines:
            return
        if opacity is None:
            opacity = getattr(self._ocr_panel, "_opacity_slider",
                              type("_", (), {"value": lambda s: 100})()).value() / 100.0
        if bg_white is None:
            bg_white = getattr(self._ocr_panel, "_chk_mask",
                               type("_", (), {"isChecked": lambda s: False})()).isChecked()
        img_w = self._pending_ocr_img_w
        img_h = self._pending_ocr_img_h
        items = []
        for ln in self._pending_ocr_lines:
            if not ln["text"].strip():
                continue
            _nx = ln["x"] / img_w
            _nw = max(ln["w"] / img_w, 0.01)
            _nw = min(_nw, 1.0 - _nx)   # clamp to right page edge
            items.append({
                "text":  ln["text"],
                "nx":    _nx,
                "ny":    ln["y"] / img_h,
                "nw":    _nw,
                "nh":    max(ln["h"] / img_h, 0.005),
                "color": ln.get("color", "#000000"),
            })
        self._viewer.set_ocr_overlay(items, opacity, bg_white)

    def _on_ocr_overlay_resized(self, items: list) -> None:
        """Called when the user drags the resize handle of an OCR preview block."""
        for i, item in enumerate(items):
            self._ocr_overlay_widths[i] = item["nw"]

    def _on_ocr_overlay_requested(
        self, lines: list, img_w: int, img_h: int, bg_white: bool, opacity: float
    ) -> None:
        """Embed OCR lines as text annotations in the PDF, matching position/size/color."""
        if not lines or not self._document.is_open:
            return

        page_idx = self._viewer.current_page

        # Remove any previous OCR overlay on this page before adding new ones
        self._form_manager.remove_ocr_annotations(page_idx)

        # Page dimensions in points (zoom=1 → pixels at 96dpi, ×72/96 → points)
        _px_w, px_h = self._renderer.get_page_size(page_idx, zoom=1.0)
        page_h_pt = px_h * 72.0 / 96.0
        page_w_pt = _px_w * 72.0 / 96.0

        from PySide6.QtCore import QRectF

        count = 0
        invisible_lines: list = []   # for Tr-3 content stream layer

        for i, ln in enumerate(lines):
            if not ln["text"].strip():
                continue

            norm_x = ln["x"] / img_w
            norm_y = ln["y"] / img_h

            # Font size in points: prefer hOCR x_size (em-height in px, calibrated by
            # Tesseract) — converts directly to points via page_h_pt/img_h scale.
            # Fallback to bbox height with empirical factor if x_size is unavailable.
            x_size = ln.get("x_size", 0.0)
            if x_size > 0:
                font_size = max(6, round(x_size * page_h_pt / img_h))
            else:
                font_size = max(6, round((ln["h"] / img_h) * page_h_pt * 0.9))

            # Add one average character width (≈0.6× em) on the right so the last
            # character is never clipped by the annotation box boundary.
            _char_padding = (font_size * 0.6) / page_w_pt if page_w_pt > 0 else 0.01
            _base_norm_w = max(min(ln["w"] / img_w + _char_padding, 1.0 - norm_x), 0.01)

            # Use user-overridden width if the block was resized in the preview; always clamp.
            norm_w = min(self._ocr_overlay_widths.get(i, _base_norm_w), 1.0 - norm_x)

            # Box height: sized to contain exactly one line at the detected font size.
            norm_h = max(font_size * _LINE_HEIGHT_RATIO / page_h_pt, ln["h"] / img_h * 1.1, 0.008)

            name = f"_ocr_{page_idx}_{i}"
            norm_rect = QRectF(norm_x, norm_y, norm_w, norm_h)
            self._form_manager.add_field(
                name, "texte", norm_rect, page_idx, [ln["text"]],
                font_size=font_size,
                color=ln.get("color", "#000000"),
                opacity=opacity,
                bg_white=bg_white,
                no_wrap=True,
                is_ocr=True,
            )
            invisible_lines.append({
                "text": ln["text"],
                "norm_x": norm_x, "norm_y": norm_y,
                "norm_h": norm_h, "font_size": font_size,
            })
            count += 1

        # Inject invisible text layer (Tr 3) into the page content stream
        # so the text is truly searchable/extractable (not just in annotations).
        if invisible_lines:
            from core.content_injector import inject_invisible_text_layer
            inject_invisible_text_layer(self._document.pdf, page_idx, invisible_lines)

        # Reset overrides for next OCR run
        self._ocr_overlay_widths.clear()

        self._reload_renderer_from_doc()
        self._viewer.refresh()
        self._update_form_overlays()
        self._document.info.is_modified = True
        self._update_title()
        self._status.showMessage(
            _("{n} ligne(s) OCR incrustée(s) sur la page.").format(n=count), 5000
        )

    # ------------------------------------------------------------------
    # Recent files
    # ------------------------------------------------------------------

    def _refresh_recent_menu(self) -> None:
        self._recent_menu.clear()
        for path in self._config.get("recent_files", []):
            a = QAction(os.path.basename(path), self)
            a.setToolTip(path)
            a.triggered.connect(lambda checked, p=path: self.open_file(p))
            self._recent_menu.addAction(a)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _update_title(self) -> None:
        if self._document.is_open:
            modified = " *" if self._document.info.is_modified else ""
            self.setWindowTitle(f"{self._document.info.title}{modified} — PDF Editor")
        else:
            self.setWindowTitle("PDF Editor")

    def _update_actions(self) -> None:
        has_doc = self._document.is_open
        if hasattr(self, "_action_undo"):
            self._action_undo.setEnabled(self._history.can_undo)
            self._action_undo.setText(
                _("Annuler : {desc}").format(desc=self._history.undo_description) if self._history.can_undo else _("Annuler")
            )
            self._action_redo.setEnabled(self._history.can_redo)
            self._action_redo.setText(
                _("Rétablir : {desc}").format(desc=self._history.redo_description) if self._history.can_redo else _("Rétablir")
            )

    def _resolve_current_text(self, page: int, original_text: str) -> str:
        """Follow the edit chain to find the current text for a word on a page."""
        current = original_text
        for (p, old, new) in self._edit_chain:
            if p == page and old == current:
                current = new
        return current

    def _cleanup_edit_tempfile(self) -> None:
        """Delete the persistent temp file used for in-place edits."""
        if self._edit_tempfile:
            try:
                os.unlink(self._edit_tempfile)
            except Exception:
                pass
            self._edit_tempfile = None

    def _add_action(self, menu, label: str, slot, shortcut: str = "") -> QAction:
        a = QAction(label, self)
        if shortcut:
            a.setShortcut(QKeySequence(shortcut))
        a.triggered.connect(slot)
        menu.addAction(a)
        return a

    def _open_search(self) -> None:
        """Show the Search dock and focus the input."""
        self._search_dock.show()
        self._search_dock.raise_()
        self._search_panel.focus_search()

    def _open_ocr(self) -> None:
        """Show the OCR dock."""
        self._ocr_dock.show()
        self._ocr_dock.raise_()

    # ------------------------------------------------------------------
    # Form designer
    # ------------------------------------------------------------------

    def _new_blank_form(self) -> None:
        """Create a blank A4 PDF, save it, and open it in the editor."""
        path, _filt = QFileDialog.getSaveFileName(
            self, _("Nouveau formulaire vierge"), "", "PDF (*.pdf)"
        )
        if not path:
            return
        if not path.lower().endswith(".pdf"):
            path += ".pdf"
        try:
            import pikepdf
            pdf = pikepdf.new()
            page = pdf.make_indirect(pikepdf.Dictionary(
                Type=pikepdf.Name.Page,
                MediaBox=pikepdf.Array([0, 0, 595, 842]),
                Resources=pikepdf.Dictionary(),
            ))
            pdf.pages.append(pikepdf.Page(page))
            pdf.save(path)
            self.open_file(path)
            self._right_dock.show()
        except Exception as exc:
            QMessageBox.critical(self, _("Erreur"), str(exc))

    def _on_form_design_mode(self, active: bool) -> None:
        """Switch viewer tool to form_design or back to select. Syncs both buttons."""
        if self._form_design_syncing:
            return
        self._form_design_syncing = True
        try:
            if not self._document.is_open:
                self._form_panel.exit_design_mode()
                self._pages_toolbar.set_design_mode(False)
                return
            self._right_dock.show()
            self._viewer.set_tool("form_design" if active else "select")
            self._pages_toolbar.set_design_mode(active)
            self._form_panel.set_design_mode(active)
            if active:
                self._left_tool_panel.deselect_all()
        finally:
            self._form_design_syncing = False

    def _on_form_field_drawn(self, norm_rect: QRectF) -> None:
        """User drew a rectangle in form_design mode — show dialog and create field."""
        self._form_panel.exit_design_mode()
        self._viewer.set_tool("select")
        try:
            dlg = AddFieldDialog(self)
            if dlg.exec() != AddFieldDialog.DialogCode.Accepted:
                return
            name = dlg.field_name()
            if not name:
                self._status.showMessage(_("Nom de champ vide — champ non créé."), 3000)
                return
            if self._form_manager.field_name_exists(name):
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(
                    self,
                    _("Nom déjà utilisé"),
                    _("Un champ nommé « {name} » existe déjà dans ce document.\n"
                      "Choisissez un autre identifiant.").format(name=name),
                )
                return
            ftype   = dlg.field_type()
            options = dlg.field_options()
            page_idx = self._viewer.current_page

            # Images use the interactive overlay flow (resize/position before commit)
            if ftype == "image":
                self._place_image_from_form(options[0] if options else "", norm_rect, page_idx)
                return

            extra = {}
            if ftype in ("label", "texte"):
                extra["font_size"]      = dlg.field_font_size()
                extra["bold"]           = dlg.field_bold()
                extra["italic"]         = dlg.field_italic()
                extra["underline"]      = dlg.field_underline()
                extra["color"]          = dlg.field_color()
                extra["letter_spacing"] = dlg.field_letter_spacing()
                if ftype == "texte":
                    extra["bg_white"] = dlg.field_bg_white()
            self._form_manager.add_field(name, ftype, norm_rect, page_idx, options, **extra)
            self._form_panel.load_form(self._form_manager)
            self._update_form_overlays()
            self._document.info.is_modified = True
            self._update_title()
            # Labels and text blocks modify the page content — reload renderer immediately.
            if ftype in ("label", "texte"):
                self._reload_renderer_from_doc()
                self._viewer.refresh()
            self._status.showMessage(
                _("Champ « {name} » ({type}) ajouté.").format(name=name, type=ftype), 4000
            )
        except Exception as exc:
            import traceback; traceback.print_exc()
            QMessageBox.critical(self, _("Erreur"), str(exc))

    def _place_image_from_form(self, image_path: str, norm_rect: QRectF, page_idx: int) -> None:
        """Place an image via the interactive overlay (resize/move then confirm)."""
        if not image_path:
            self._status.showMessage(_("Chemin d'image manquant."), 3000)
            return
        try:
            from PIL import Image as PilImage
            import pikepdf
            _raw = PilImage.open(image_path)
            src_img = (_raw.convert("RGBA") if _raw.mode in ("RGBA", "LA", "PA")
                       else _raw.convert("RGB"))
        except Exception as exc:
            QMessageBox.warning(self, _("Erreur"),
                                _("Impossible de lire l'image :\n{err}").format(err=exc))
            return

        page = self._document.pdf.pages[page_idx]
        try:
            xobjects = page.Resources.get("/XObject", pikepdf.Dictionary())
        except Exception:
            xobjects = pikepdf.Dictionary()
        existing = set(str(k) for k in xobjects.keys())
        n = 1
        while f"/NewImg{n}" in existing:
            n += 1
        xobj_name = f"NewImg{n}"

        placeholder = pikepdf.Stream(self._document.pdf, b"")
        placeholder["/Type"]             = pikepdf.Name("/XObject")
        placeholder["/Subtype"]          = pikepdf.Name("/Image")
        placeholder["/Width"]            = pikepdf.Integer(1)
        placeholder["/Height"]           = pikepdf.Integer(1)
        placeholder["/ColorSpace"]       = pikepdf.Name("/DeviceRGB")
        placeholder["/BitsPerComponent"] = pikepdf.Integer(8)
        xobjects[f"/{xobj_name}"] = placeholder
        if "/XObject" not in page.Resources:
            page.Resources["/XObject"] = xobjects

        self._pending_replace = (page_idx, xobj_name, src_img)
        self._last_clicked_img = {
            "name": xobj_name,
            "x": norm_rect.x(), "y": norm_rect.y(),
            "width": norm_rect.width(), "height": norm_rect.height(),
        }
        self._viewer.show_image_overlay(src_img, norm_rect)
        self._document.info.is_modified = True
        self._update_title()
        self.statusBar().showMessage(
            _("Redimensionnez / déplacez l'image puis cliquez ✓ Valider."), 0
        )

    def _on_context_menu(self, ann: dict, gx: int, gy: int) -> None:
        """Show a right-click context menu for an annotation."""
        from PySide6.QtWidgets import QMenu
        from PySide6.QtCore import QPoint
        ann_type = ann.get("type", "")
        ann_id   = ann.get("id", "")
        menu = QMenu(self)

        def _erase():
            r = QRectF(
                ann["x"] - 0.001, ann["y"] - 0.001,
                ann.get("width", 0.01) + 0.002, ann.get("height", 0.01) + 0.002,
            )
            self._on_annotation_erase_requested(r)

        if ann_type == "comment":
            menu.addAction(_("Modifier le commentaire"), lambda: self._on_comment_edit(ann_id))
            menu.addSeparator()
        elif ann_type == "freetext":
            menu.addAction(_("Modifier le texte"), lambda: self._on_text_edit_by_ann(ann))
            menu.addSeparator()
        elif ann_type == "image":
            w, h = self.width() or 1, self.height() or 1
            cx = ann["x"] + ann.get("width", 0) / 2
            cy = ann["y"] + ann.get("height", 0) / 2
            menu.addAction(_("Remplacer l'image"), lambda: self._on_image_click(cx, cy))
            menu.addSeparator()

        menu.addAction(_("Supprimer"), _erase)
        menu.exec(QPoint(gx, gy))

    def _delete_injected_block(self, page_idx: int, block_id: str) -> None:
        """Remove a _BEGIN_PDFED injected block from the PDF stream."""
        from core.content_injector import remove_injected_block
        ok = remove_injected_block(self._document.pdf, page_idx, block_id)
        if ok:
            self._injected_meta.pop(block_id, None)
            # Remove from _injected_blocks lookup too
            self._injected_blocks = {k: v for k, v in self._injected_blocks.items() if v != block_id}
            # Clear block ghost if it was this block
            self._viewer._page_widget._block_drag_current = None
            self._viewer._page_widget._block_drag_ghost = None
            self._reload_renderer_from_doc()
            self._cache.invalidate(page_idx)
            self._viewer.refresh()
            self._document.info.is_modified = True
            self._update_title()
            self._update_actions()
            self._status.showMessage(_("Bloc supprimé. Enregistrez pour sauvegarder."))

    def _hide_native_text(self, page_idx: int, block, nr: dict, ph: float) -> None:
        """Cover native PDF text with a white rectangle (non-destructive hide)."""
        from core.content_injector import inject_text_block
        import time as _t
        block_id = f"b{int(_t.time() * 1000)}"
        _ch = nr["height"]
        _orig_fs_norm = block.font_size / ph
        _margin_y_top = max(_orig_fs_norm * 0.85, _ch * 0.1, 0.003)
        _margin_y_bot = max(_orig_fs_norm * 0.25, 0.002)
        _margin_x = 0.005
        _cover_nx = max(0.0, nr["x"] - _margin_x)
        _cover_ny = max(0.0, nr["y"] - _margin_y_top)
        _cover_nw = nr["width"] + 2 * _margin_x
        _cover_nh = _ch + _margin_y_top + _margin_y_bot
        ok = inject_text_block(
            self._document.pdf, page_idx, block_id,
            cover_nx=_cover_nx, cover_ny=_cover_ny,
            cover_nw=_cover_nw, cover_nh=_cover_nh,
            text_nx=nr["x"], text_ny=nr["y"],
            text_nw=nr["width"], text_nh=_ch,
            text="", font_size=block.font_size,
        )
        if ok:
            self._injected_meta[block_id] = {
                "text": "", "font_size": block.font_size,
                "bold": False, "italic": False, "color": "#000000",
                "font_family": "Helvetica", "bg_color": "",
                "letter_spacing": 0.0,
                "cover_nx": _cover_nx, "cover_ny": _cover_ny,
                "cover_nw": _cover_nw, "cover_nh": _cover_nh,
                "text_nw": nr["width"],
            }
            self._reload_renderer_from_doc()
            self._cache.invalidate(page_idx)
            self._viewer.refresh()
            self._document.info.is_modified = True
            self._update_title()
            self._update_actions()
            self._status.showMessage(_("Texte masqué. Enregistrez pour sauvegarder."))

    def _delete_native_text(self, page_idx: int, block) -> None:
        """Supprime un texte natif directement du flux PDF (suppression réelle, pas rectangle blanc)."""
        from core.content_injector import delete_native_text_block
        ok = delete_native_text_block(self._document.pdf, page_idx, block)
        if ok:
            self._reload_renderer_from_doc()
            self._cache.invalidate(page_idx)
            self._viewer.refresh()
            self._document.info.is_modified = True
            self._update_title()
            self._update_actions()
            self._status.showMessage(_("Texte supprimé du flux. Enregistrez pour sauvegarder."))
        else:
            self._status.showMessage(_("Impossible de supprimer ce texte du flux."))

    def _on_text_edit_by_ann(self, ann: dict) -> None:
        """Open text edit popup centred on an existing freetext annotation."""
        cx = ann["x"] + ann.get("width", 0) / 2
        cy = ann["y"] + ann.get("height", 0) / 2
        self._on_text_edit_requested(cx, cy)

    def _update_form_overlays(self, _page_idx: int = -1) -> None:
        """Refresh green field overlays (fields + labels) on the current page."""
        # Clear OCR Qt preview when navigating to a different page
        self._pending_ocr_lines = []
        self._viewer.clear_ocr_overlay()
        if not self._document.is_open:
            self._viewer.set_form_overlays([])
            return
        page_idx = self._viewer.current_page
        overlays = []
        if self._form_manager.has_form():
            overlays = self._form_manager.get_form_overlays_for_page(page_idx)
            for ov in overlays:
                ov.setdefault("kind", "field")
        labels = self._form_manager.get_all_labels_for_page(page_idx)
        self._viewer.set_form_overlays(overlays + labels)

    def _on_form_element_moved(self, kind: str, name: str,
                                new_nx: float, new_ny: float,
                                nw: float, nh: float) -> None:
        """Persist a form element (label or field) move to the pikepdf document."""
        page_idx = self._viewer.current_page
        if kind == "label":
            # Retrieve current text and formatting before removing the old annotation
            labels = self._form_manager.get_all_labels_for_page(page_idx)
            label = next((lb for lb in labels if lb["name"] == name), None)
            text = label["text"] if label else name
            orig_ftype = label.get("ftype", "label") if label else "label"
            fmt = self._form_manager.get_label_formatting(page_idx, name)
            self._form_manager.add_field(
                name, orig_ftype, QRectF(new_nx, new_ny, nw, nh), page_idx, [text],
                font_size=fmt["font_size"],
                bold=fmt["bold"],
                italic=fmt["italic"],
                color=fmt.get("color", "#000000"),
                underline=fmt.get("underline", False),
                letter_spacing=fmt.get("letter_spacing", 0.0),
                bg_color=fmt.get("bg_color", ""),
                bg_white=fmt.get("bg_white", False),
                is_ocr=label.get("is_ocr", False) if label else False,
            )
            self._reload_renderer_from_doc()
            self._viewer.refresh()
        else:
            self._form_manager.move_field(page_idx, name, new_nx, new_ny, nw, nh)
            self._reload_renderer_from_doc()
            self._viewer.refresh()
        self._update_form_overlays()
        self._document.info.is_modified = True
        self._update_title()

    def _on_search_result(self, page_idx: int, matched_text: str) -> None:
        """Navigate to page and highlight the matched text."""
        self._viewer.display_page(page_idx)
        query = self._search_panel.current_query
        case_sensitive = self._search_panel.is_case_sensitive
        if not query or not self._document.path:
            return
        try:
            import pdfplumber
            from PySide6.QtCore import QRectF as _QRectF
            with pdfplumber.open(self._document.path) as pdf:
                page = pdf.pages[page_idx]
                pw, ph = page.width, page.height
                # pdfplumber >= 0.6 has page.search()
                try:
                    results = page.search(query, regex=False, case=case_sensitive)
                except (AttributeError, TypeError):
                    results = []
                if results:
                    r = results[0]
                    rect = _QRectF(
                        r["x0"] / pw, r["top"] / ph,
                        (r["x1"] - r["x0"]) / pw,
                        (r["bottom"] - r["top"]) / ph,
                    )
                    self._viewer.highlight_search(rect)
                    return
                # Fallback: word-level search
                words = page.extract_words()
                cmp_q = query if case_sensitive else query.lower()
                for w in words:
                    cmp_w = w["text"] if case_sensitive else w["text"].lower()
                    if cmp_q in cmp_w:
                        rect = _QRectF(
                            w["x0"] / pw, w["top"] / ph,
                            (w["x1"] - w["x0"]) / pw,
                            (w["bottom"] - w["top"]) / ph,
                        )
                        self._viewer.highlight_search(rect)
                        return
        except Exception:
            pass  # highlight best-effort only

    def keyPressEvent(self, event) -> None:
        from PySide6.QtCore import Qt as _Qt
        if event.key() == _Qt.Key.Key_Delete and not event.modifiers():
            if self._last_deletable:
                self._delete_last_selected()
                event.accept()
                return
        super().keyPressEvent(event)

    def _delete_last_selected(self) -> None:
        """Delete the element that was last right-clicked."""
        item = self._last_deletable
        if not item:
            self._status.showMessage(
                _("Clic droit sur un élément pour le sélectionner, puis Suppr pour l'effacer."), 3000
            )
            return
        t = item["type"]
        if t == "annotation":
            ann = item["ann"]
            r = QRectF(
                ann["x"] - 0.001, ann["y"] - 0.001,
                ann.get("width", 0.01) + 0.002, ann.get("height", 0.01) + 0.002,
            )
            self._on_annotation_erase_requested(r)
        elif t == "label":
            self._label_delete(item["page_idx"], item["name"])
        elif t == "block":
            self._delete_injected_block(item["page_idx"], item["block_id"])
        self._last_deletable = None

    def _delete_current_page(self) -> None:
        if not self._document.is_open:
            return
        if not self._ensure_owner_access():
            return
        if self._document.page_count <= 1:
            QMessageBox.warning(
                self, _("Supprimer la page"),
                _("Impossible de supprimer l'unique page du document."),
            )
            return
        page_idx = self._viewer.current_page
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Icon.Question)
        box.setWindowTitle(_("Supprimer la page"))
        box.setText(_("Supprimer la page {n} du document ?").format(n=page_idx + 1))
        btn_yes = box.addButton(_("Supprimer"), QMessageBox.ButtonRole.DestructiveRole)
        box.addButton(_("Annuler"), QMessageBox.ButtonRole.RejectRole)
        box.exec()
        if box.clickedButton() != btn_yes:
            return
        # Snapshot annotations state for undo
        all_anns_before = list(self._annotations.get_all())

        def _do_delete():
            # Renumber annotations
            self._annotations.clear()
            for ann in all_anns_before:
                if ann.page == page_idx:
                    continue
                if ann.page > page_idx:
                    ann.page -= 1
                self._annotations.add(ann)
            self._document.delete_page(page_idx)

        def _undo_delete():
            # Restore annotations as they were
            self._annotations.clear()
            for ann in all_anns_before:
                self._annotations.add(ann)

        def _refresh_delete():
            self._reload_renderer_from_doc()
            self._cache.clear()
            new_page = min(page_idx, self._document.page_count - 1)
            self._sidebar.load_thumbnails(self._renderer)
            self._viewer.display_page(new_page)
            self._document.info.is_modified = True
            self._update_title()

        cmd = PdfStructureCommand(
            self._document.pdf, _do_delete,
            f"Supprimer page {page_idx + 1}",
            _refresh_delete,
        )
        # Override undo to also restore annotations
        _orig_undo = cmd.undo
        def _full_undo():
            _undo_delete()
            _orig_undo()
        cmd.undo = _full_undo  # type: ignore[method-assign]

        self._history.push(cmd)
        self._update_actions()
        self._status.showMessage(_("Page {n} supprimée.").format(n=page_idx + 1))

    def _print_document(self) -> None:
        if not self._document.is_open:
            return
        from PySide6.QtPrintSupport import QPrinter, QPrintDialog
        from PySide6.QtGui import QPainter
        from PySide6.QtCore import Qt as _Qt

        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        dlg = QPrintDialog(printer, self)
        if dlg.exec() != QPrintDialog.DialogCode.Accepted:
            return

        page_count = self._document.page_count
        from_p = printer.fromPage()
        to_p = printer.toPage()
        pages = range(page_count) if from_p == 0 else range(from_p - 1, min(to_p, page_count))

        # Render at ~3× zoom for decent print quality
        zoom = min(printer.resolution() / 72.0, 4.0)

        painter = QPainter(printer)
        first = True
        for page_idx in pages:
            img = self._renderer.render_page(page_idx, zoom=zoom)
            if img is None:
                continue
            if not first:
                printer.newPage()
            first = False
            pixmap = QPixmap.fromImage(img)
            rect = painter.viewport()
            scaled = pixmap.scaled(
                rect.size(),
                _Qt.AspectRatioMode.KeepAspectRatio,
                _Qt.TransformationMode.SmoothTransformation,
            )
            x = (rect.width() - scaled.width()) // 2
            y = (rect.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)
        painter.end()

    def _shell_integration(self) -> None:
        from utils.shell_integration import (
            is_registered, register, unregister,
            is_combine_registered, register_combine, unregister_combine,
        )
        from PySide6.QtWidgets import (
            QDialog, QVBoxLayout, QLabel, QPushButton, QDialogButtonBox,
            QFrame, QHBoxLayout,
        )

        dlg = QDialog(self)
        dlg.setWindowTitle(_("Intégration Windows — clic droit"))
        dlg.setMinimumWidth(460)
        layout = QVBoxLayout(dlg)
        layout.setSpacing(12)

        img_exts     = "JPG · JPEG · PNG · BMP · TIFF · TIF · WebP"
        combine_exts = "PDF · JPG · JPEG · PNG · BMP · TIFF · TIF · WebP"

        # ── Section 1 : Transformer en PDF ──────────────────────────────
        def _make_section(title: str, desc: str, is_active_fn, toggle_on_fn,
                          toggle_off_fn, on_msg: str, off_msg: str):
            frame = QFrame()
            frame.setFrameShape(QFrame.Shape.StyledPanel)
            fl = QVBoxLayout(frame)
            fl.setSpacing(6)

            lbl_title = QLabel(f"<b>{title}</b>")
            lbl_title.setTextFormat(Qt.TextFormat.RichText)
            fl.addWidget(lbl_title)

            active = is_active_fn()
            status_lbl = QLabel(_("✅ Actif") if active else _("❌ Inactif"))
            fl.addWidget(status_lbl)

            lbl_desc = QLabel(desc)
            lbl_desc.setWordWrap(True)
            lbl_desc.setTextFormat(Qt.TextFormat.RichText)
            fl.addWidget(lbl_desc)

            btn_row = QHBoxLayout()
            btn_row.addStretch()
            toggle_btn = QPushButton(_("Désactiver") if active else _("Activer"))
            btn_row.addWidget(toggle_btn)
            fl.addLayout(btn_row)

            def _toggle():
                if is_active_fn():
                    toggle_off_fn()
                    toggle_btn.setText(_("Activer"))
                    status_lbl.setText(_("❌ Inactif"))
                    QMessageBox.information(dlg, _("Intégration Windows"), off_msg)
                else:
                    try:
                        toggle_on_fn()
                        toggle_btn.setText(_("Désactiver"))
                        status_lbl.setText(_("✅ Actif"))
                        QMessageBox.information(dlg, _("Intégration Windows"), on_msg)
                    except Exception as exc:
                        QMessageBox.critical(dlg, _("Erreur"), str(exc))

            toggle_btn.clicked.connect(_toggle)
            return frame

        layout.addWidget(_make_section(
            title=_("🖼  Transformer une image en PDF"),
            desc=_(
                "Lorsque l'intégration est active, un clic droit sur un fichier image "
                "({exts}) dans l'explorateur Windows propose l'option "
                "<b>Transformer en PDF</b>. Le PDF est créé dans le même dossier "
                "que l'image."
            ).format(exts=img_exts),
            is_active_fn=is_registered,
            toggle_on_fn=register,
            toggle_off_fn=unregister,
            on_msg=_(
                "Clic droit activé !\n\n"
                "Faites un clic droit sur n'importe quelle image "
                "({exts}) dans l'explorateur pour convertir en PDF."
            ).format(exts=img_exts),
            off_msg=_("Clic droit désactivé pour les fichiers images."),
        ))

        layout.addWidget(_make_section(
            title=_("📎  Combiner des fichiers dans PDF Editor"),
            desc=_(
                "Lorsque l'intégration est active, une sélection multiple de fichiers "
                "({exts}) dans l'explorateur Windows propose l'option "
                "<b>Combiner dans PDF Editor</b>. Le dialogue de réorganisation "
                "s'ouvre avec ces fichiers pré-chargés."
            ).format(exts=combine_exts),
            is_active_fn=is_combine_registered,
            toggle_on_fn=register_combine,
            toggle_off_fn=unregister_combine,
            on_msg=_(
                "Combinaison activée !\n\n"
                "Sélectionnez plusieurs fichiers ({exts}) dans l'explorateur,\n"
                "faites un clic droit et choisissez «\u202fCombiner dans PDF Editor\u202f»."
            ).format(exts=combine_exts),
            off_msg=_("Clic droit «\u202fCombiner\u202f» désactivé."),
        ))

        close_btn = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        close_btn.rejected.connect(dlg.reject)
        layout.addWidget(close_btn)

        dlg.exec()

    def _open_help(self) -> None:
        from ui.dialogs.help_dialog import HelpDialog
        dlg = HelpDialog(self)
        dlg.exec()

    def _help_pfx(self) -> None:
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QDialogButtonBox
        dlg = QDialog(self)
        dlg.setWindowTitle(_("Obtenir un certificat de signature .pfx"))
        dlg.setMinimumWidth(560)
        layout = QVBoxLayout(dlg)
        txt = QTextEdit()
        txt.setReadOnly(True)
        txt.setTextInteractionFlags(
            txt.textInteractionFlags() |
            Qt.TextInteractionFlag.TextSelectableByMouse |
            Qt.TextInteractionFlag.TextSelectableByKeyboard
        )
        txt.setHtml(_(
            "<b>Certificat de signature numérique (.pfx / .p12)</b><br><br>"
            "Pour que la signature soit vérifiable par des tiers, il faut un certificat "
            "émis par une <b>Autorité de Certification (CA) reconnue</b>.<br><br>"
            "<b>Fournisseurs courants :</b><br>"
            "• <b>Certum</b> (Asseco) — certum.eu<br>"
            "• <b>Sectigo</b> — sectigo.com<br>"
            "• <b>GlobalSign</b> — globalsign.com<br>"
            "• <b>DigiCert</b> — digicert.com<br><br>"
            "<b>Coût :</b> 50 – 200 €/an selon le niveau de validation.<br>"
            "Le fournisseur livre directement un fichier <b>.pfx</b> (ou .p12) "
            "protégé par un mot de passe.<br><br>"
            "<i>Pour un usage interne uniquement, vous pouvez générer un certificat "
            "auto-signé avec OpenSSL :</i><br><br>"
            "<tt>openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes<br>"
            "openssl pkcs12 -export -out cert.pfx -inkey key.pem -in cert.pem</tt>"
        ))
        txt.setFixedHeight(260)
        layout.addWidget(txt)
        btn = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        btn.rejected.connect(dlg.accept)
        layout.addWidget(btn)
        dlg.exec()

    def _report_bug(self) -> None:
        import webbrowser
        webbrowser.open("https://github.com/Leteint/pdf-editor/issues/new?template=bug_report.yml")

    def _suggest_feature(self) -> None:
        import webbrowser
        webbrowser.open("https://github.com/Leteint/pdf-editor/issues/new?template=feature_request.yml")

    def _manage_license(self) -> None:
        from utils.license import get_stored_key, check_license, clear_license
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QDialogButtonBox, QPushButton, QHBoxLayout

        key = get_stored_key()
        dlg = QDialog(self)
        dlg.setWindowTitle(_("Licence — PDF Editor"))
        dlg.setMinimumWidth(420)
        lay = QVBoxLayout(dlg)
        lay.setSpacing(12)

        if key:
            result = check_license(key)
            color  = "#60c060" if result.valid else "#e07050"
            icon   = "✅" if result.valid else "❌"
            short_key = key[:8] + "…" + key[-4:] if len(key) > 16 else key
            lay.addWidget(QLabel(
                f"<b>{_('Clé de licence :')}</b> <tt>{short_key}</tt><br>"
                f"<b>{_('Statut :')}</b> <span style='color:{color}'>{icon} {result.reason}</span>"
            ))
            lbl = lay.itemAt(0).widget()
            lbl.setTextFormat(Qt.TextFormat.RichText)
            lbl.setWordWrap(True)

            btn_row = QHBoxLayout()
            btn_deactivate = QPushButton("🗑  " + _("Désactiver cette licence"))
            btn_deactivate.setStyleSheet("color: #e07050;")

            def _deactivate():
                box = QMessageBox(dlg)
                box.setIcon(QMessageBox.Icon.Question)
                box.setWindowTitle(_("Désactiver la licence"))
                box.setText(_("Supprimer la licence de cet ordinateur ?\n\nVous pourrez la réactiver sur un autre poste."))
                box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if box.exec() == QMessageBox.StandardButton.Yes:
                    clear_license()
                    QMessageBox.information(dlg, _("Licence"), _("Licence désactivée sur cet ordinateur."))
                    dlg.accept()

            btn_deactivate.clicked.connect(_deactivate)
            btn_row.addStretch()
            btn_row.addWidget(btn_deactivate)
            lay.addLayout(btn_row)
        else:
            lay.addWidget(QLabel(_("Aucune licence activée sur cet ordinateur.")))
            from ui.dialogs.license_dialog import LicenseDialog

            def _activate():
                dlg.accept()
                lic_dlg = LicenseDialog(self)
                lic_dlg.exec()

            btn_activate = QPushButton("🔑  " + _("Entrer une clé de licence"))
            btn_activate.clicked.connect(_activate)
            lay.addWidget(btn_activate)

        close_btn = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        close_btn.rejected.connect(dlg.reject)
        lay.addWidget(close_btn)
        dlg.exec()

    def _about(self) -> None:
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QDialogButtonBox
        from PySide6.QtCore import Qt

        dlg = QDialog(self)
        dlg.setWindowTitle(_("À propos de PDF Editor"))
        dlg.setMinimumWidth(420)
        lay = QVBoxLayout(dlg)
        lay.setSpacing(12)

        lbl = QLabel(
            "<div style='text-align:center;'>"
            "<h2 style='margin-bottom:2px;'>PDF Editor</h2>"
            "<p style='color:#888; margin-top:0;'>Version 1.3.0 &nbsp;·&nbsp; 2026</p>"
            "</div>"
            "<hr>"
            "<p>"
            "Éditeur PDF complet : lecture, modification, annotations, formulaires, OCR,<br>"
            "tampons, signatures numériques, fusion, fractionnement et bien plus."
            "</p>"
            "<hr>"
            "<p><b>Technologies open source utilisées :</b><br>"
            "<small>"
            "PySide6 (Qt) &nbsp;·&nbsp; pikepdf &nbsp;·&nbsp; pdfplumber &nbsp;·&nbsp; "
            "pypdf &nbsp;·&nbsp; pyHanko &nbsp;·&nbsp; pdfium2 &nbsp;·&nbsp; "
            "Tesseract OCR &nbsp;·&nbsp; img2pdf"
            "</small></p>"
            "<hr>"
            "<p style='text-align:center;'>"
            "<b>Support &amp; assistance :</b><br>"
            "<a href='https://pdfeditor.lemonsqueezy.com'>pdfeditor.lemonsqueezy.com</a>"
            "</p>"
            "<p style='text-align:center; color:#888;'><small>"
            "© 2026 — Tous droits réservés"
            "</small></p>"
        )
        lbl.setOpenExternalLinks(True)
        lbl.setWordWrap(True)
        lbl.setTextFormat(Qt.TextFormat.RichText)
        lay.addWidget(lbl)

        btn = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        btn.accepted.connect(dlg.accept)
        lay.addWidget(btn)

        dlg.exec()

    # ------------------------------------------------------------------
    # Close event
    # ------------------------------------------------------------------

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._document.is_open and self._document.info.is_modified:
            box = QMessageBox(self)
            box.setIcon(QMessageBox.Icon.Question)
            box.setWindowTitle(_("Quitter"))
            box.setText(_("Le document a des modifications non enregistrées. Quitter quand même ?"))
            btn_quit = box.addButton(_("Quitter sans enregistrer"), QMessageBox.ButtonRole.DestructiveRole)
            box.addButton(_("Annuler"), QMessageBox.ButtonRole.RejectRole)
            box.exec()
            if box.clickedButton() != btn_quit:
                event.ignore()
                return
        self._cleanup_edit_tempfile()
        self._renderer.close()
        event.accept()

    # ------------------------------------------------------------------
    # Language
    # ------------------------------------------------------------------

    def _change_language(self, lang_code: str) -> None:
        """Save the chosen language to config and propose a restart."""
        if lang_code == get_language():
            return
        self._config.set("language", lang_code)
        display_name = SUPPORTED_LANGUAGES.get(lang_code, lang_code)
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Icon.Question)
        box.setWindowTitle(_("Appliquer la langue"))
        box.setText(_("Redémarrer pour appliquer la langue « {lang} » ?").format(lang=display_name))
        btn_restart = box.addButton(_("Redémarrer"), QMessageBox.ButtonRole.AcceptRole)
        box.addButton(_("Annuler"), QMessageBox.ButtonRole.RejectRole)
        box.setDefaultButton(btn_restart)
        box.exec()
        if box.clickedButton() == btn_restart:
            import subprocess, sys
            self._cleanup_edit_tempfile()
            self._renderer.close()
            subprocess.Popen([sys.executable] + sys.argv)
            QApplication.quit()
        else:
            self._status.showMessage(_("La langue sera appliquée au prochain démarrage."), 5000)
