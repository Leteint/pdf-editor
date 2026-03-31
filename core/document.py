"""
Document model — central state for an open PDF.
Uses pikepdf for manipulation and pypdf for metadata.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Optional

import pikepdf
from pypdf import PdfReader


@dataclass
class DocumentInfo:
    title: str = ""
    author: str = ""
    subject: str = ""
    creator: str = ""
    page_count: int = 0
    file_path: str = ""
    file_size: int = 0
    is_encrypted: bool = False
    is_modified: bool = False


class Document:
    """
    Central document model.
    Holds the pikepdf.Pdf instance and exposes high-level operations.
    """

    def __init__(self) -> None:
        self._pdf: Optional[pikepdf.Pdf] = None
        self._path: Optional[str] = None
        self._info = DocumentInfo()
        self._password: Optional[str] = None
        self._owner_unlocked: bool = False  # True once opened with the owner password

    # ------------------------------------------------------------------
    # Open / Close
    # ------------------------------------------------------------------

    def load(self, path: str, password: str = "") -> None:
        """Open a PDF file. Raises on error."""
        if self._pdf:
            self.close()

        try:
            self._pdf = pikepdf.open(path, password=password or "", allow_overwriting_input=True)
        except pikepdf.PasswordError:
            raise ValueError("Mot de passe incorrect ou fichier chiffré.")
        except Exception as exc:
            raise RuntimeError(f"Impossible d'ouvrir le fichier : {exc}") from exc

        self._path = path
        self._password = password
        # If a non-empty password was supplied assume owner access; otherwise unknown.
        self._owner_unlocked = bool(password)
        self._load_info()

    def try_unlock_as_owner(self, password: str) -> bool:
        """Reopen with the owner password for full modification access. Returns True on success."""
        if not self._path:
            return False
        try:
            new_pdf = pikepdf.open(self._path, password=password, allow_overwriting_input=True)
            if self._pdf:
                self._pdf.close()
            self._pdf = new_pdf
            self._password = password
            self._owner_unlocked = True
            return True
        except pikepdf.PasswordError:
            return False

    @property
    def needs_owner_password(self) -> bool:
        """True when document is encrypted but not yet unlocked for modification."""
        return self._info.is_encrypted and not self._owner_unlocked

    def close(self) -> None:
        if self._pdf:
            self._pdf.close()
            self._pdf = None
        self._path = None
        self._info = DocumentInfo()
        self._owner_unlocked = False

    # ------------------------------------------------------------------
    # Save
    # ------------------------------------------------------------------

    def save(self, path: Optional[str] = None) -> None:
        """Save to the original path or a new path."""
        self._ensure_open()
        target = path or self._path
        if not target:
            raise ValueError("Aucun chemin de sauvegarde spécifié.")
        self._pdf.save(target)
        self._path = target
        self._info.is_modified = False

    def reopen(self, path: str, password: str = "") -> None:
        """Close the current pikepdf instance and reopen from *path*.

        Used after an atomic rename-save to refresh the in-memory document
        without losing the active path or password.
        """
        if self._pdf:
            self._pdf.close()
        self._pdf = pikepdf.open(path, password=password or "", allow_overwriting_input=True)
        self._path = path
        self._info.is_modified = False

    # ------------------------------------------------------------------
    # Page operations
    # ------------------------------------------------------------------

    @property
    def page_count(self) -> int:
        return len(self._pdf.pages) if self._pdf else 0

    def get_page(self, index: int) -> pikepdf.Page:
        self._ensure_open()
        return self._pdf.pages[index]

    def rotate_page(self, index: int, degrees: int) -> None:
        """Rotate a page by degrees (90, 180, 270)."""
        self._ensure_open()
        page = self._pdf.pages[index]
        current = int(page.get("/Rotate", 0))
        page["/Rotate"] = pikepdf.Integer((current + degrees) % 360)
        self._info.is_modified = True

    def delete_page(self, index: int) -> None:
        self._ensure_open()
        del self._pdf.pages[index]
        self._info.is_modified = True

    def move_page(self, from_index: int, to_index: int) -> None:
        self._ensure_open()
        page = self._pdf.pages[from_index]
        del self._pdf.pages[from_index]
        self._pdf.pages.insert(to_index, page)
        self._info.is_modified = True

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def info(self) -> DocumentInfo:
        return self._info

    @property
    def path(self) -> Optional[str]:
        return self._path

    @property
    def pdf(self) -> Optional[pikepdf.Pdf]:
        return self._pdf

    @property
    def is_open(self) -> bool:
        return self._pdf is not None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_info(self) -> None:
        if not self._pdf or not self._path:
            return
        meta = self._pdf.open_metadata()
        self._info.title = str(meta.get("dc:title", "")) or os.path.basename(self._path)
        self._info.author = str(meta.get("dc:creator", ""))
        self._info.subject = str(meta.get("dc:description", ""))
        self._info.page_count = len(self._pdf.pages)
        self._info.file_path = self._path
        self._info.file_size = os.path.getsize(self._path)
        self._info.is_encrypted = self._pdf.is_encrypted
        self._info.is_modified = False

    def _ensure_open(self) -> None:
        if not self._pdf:
            raise RuntimeError("Aucun document ouvert.")
