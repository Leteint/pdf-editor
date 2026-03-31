"""
Annotation model and persistence.
Annotations are stored as pikepdf annotation objects and also kept in memory.
"""
from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field, asdict
from typing import Optional, List
import pikepdf


@dataclass
class Annotation:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    page: int = 0
    type: str = "highlight"   # highlight | underline | draw | comment | freetext
    x: float = 0.0            # normalized 0-1
    y: float = 0.0
    width: float = 0.0
    height: float = 0.0
    color: str = "#FFFF00"
    text: str = ""
    stroke_width: float = 2.0

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Annotation":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


class AnnotationManager:
    """
    Manages all annotations for the current document.
    Saves them embedded in PDF (pikepdf) or as sidecar JSON.
    """

    def __init__(self) -> None:
        self._annotations: list[Annotation] = []

    def add(self, ann: Annotation) -> None:
        self._annotations.append(ann)

    def remove(self, ann_id: str) -> None:
        self._annotations = [a for a in self._annotations if a.id != ann_id]

    def get_page_annotations(self, page: int) -> List[Annotation]:
        return [a for a in self._annotations if a.page == page]

    def get_all(self) -> List[Annotation]:
        return list(self._annotations)

    def clear(self) -> None:
        self._annotations.clear()

    # ------------------------------------------------------------------
    # Persistence — embedded PDF annotations via pikepdf
    # ------------------------------------------------------------------

    # Prefix used in /NM to identify annotations written by this app.
    _NM_PREFIX = "pdfeditor:"

    def write_to_pdf(self, pdf: pikepdf.Pdf) -> None:
        """Write all annotations into the PDF structure.

        Any annotation previously written by this app (identified by the /NM
        prefix) is removed first so repeated saves don't produce duplicates.
        """
        # Remove our own annotations from every page before rewriting them.
        for page in pdf.pages:
            if "/Annots" not in page:
                continue
            kept = [
                a for a in page["/Annots"]
                if not str(a.get("/NM", "")).startswith(self._NM_PREFIX)
            ]
            page["/Annots"] = pikepdf.Array(kept)

        for ann in self._annotations:
            page = pdf.pages[ann.page]
            self._write_annotation(pdf, page, ann)

    def load_from_pdf(self, pdf: pikepdf.Pdf) -> None:
        """Reconstruct annotations previously written by this app from the PDF.

        Only annotations tagged with our /NM prefix are imported so that
        annotations added by other tools (Acrobat, etc.) are left untouched.
        """
        self.clear()
        for page_idx, page in enumerate(pdf.pages):
            if "/Annots" not in page:
                continue
            try:
                page_box = page.mediabox
                pw = float(page_box[2]) - float(page_box[0])
                ph = float(page_box[3]) - float(page_box[1])
            except Exception:
                continue
            for annot in page["/Annots"]:
                try:
                    nm = str(annot.get("/NM", ""))
                    if not nm.startswith(self._NM_PREFIX):
                        continue
                    ann_id = nm[len(self._NM_PREFIX):]
                    subtype = str(annot.get("/Subtype", ""))
                    rect = annot.get("/Rect", None)
                    if rect is None:
                        continue
                    x1, y1, x2, y2 = [float(v) for v in rect]
                    norm_x = x1 / pw
                    norm_y = 1.0 - y2 / ph
                    norm_w = (x2 - x1) / pw
                    norm_h = (y2 - y1) / ph
                    text = str(annot.get("/Contents", ""))
                    color_arr = annot.get("/C", None)
                    if color_arr:
                        r, g, b = [min(255, int(float(v) * 255)) for v in color_arr]
                        color = f"#{r:02x}{g:02x}{b:02x}"
                    else:
                        color = "#ffff00"
                    subtype_map = {
                        "/Highlight": "highlight",
                        "/Underline": "underline",
                        "/Text": "comment",
                    }
                    ann_type = subtype_map.get(subtype)
                    if ann_type is None:
                        continue
                    ann = Annotation(
                        id=ann_id,
                        page=page_idx,
                        type=ann_type,
                        x=norm_x,
                        y=norm_y,
                        width=norm_w,
                        height=norm_h,
                        color=color,
                        text=text,
                    )
                    self._annotations.append(ann)
                except Exception:
                    continue

    def _write_annotation(
        self, pdf: pikepdf.Pdf, page: pikepdf.Page, ann: Annotation
    ) -> None:
        page_box = page.mediabox
        pw = float(page_box[2]) - float(page_box[0])
        ph = float(page_box[3]) - float(page_box[1])

        x1 = ann.x * pw
        y1 = (1 - ann.y - ann.height) * ph
        x2 = (ann.x + ann.width) * pw
        y2 = (1 - ann.y) * ph

        rect = pikepdf.Array([x1, y1, x2, y2])
        color = _hex_to_pdf_color(ann.color)
        nm = pikepdf.String(f"{self._NM_PREFIX}{ann.id}")

        if ann.type == "highlight":
            annot = pikepdf.Dictionary(
                Type=pikepdf.Name("/Annot"),
                Subtype=pikepdf.Name("/Highlight"),
                NM=nm,
                Rect=rect,
                QuadPoints=pikepdf.Array([x1, y2, x2, y2, x1, y1, x2, y1]),
                C=pikepdf.Array(color),
                CA=pikepdf.Real(0.5),
                Contents=pikepdf.String(ann.text),
            )
        elif ann.type == "underline":
            annot = pikepdf.Dictionary(
                Type=pikepdf.Name("/Annot"),
                Subtype=pikepdf.Name("/Underline"),
                NM=nm,
                Rect=rect,
                QuadPoints=pikepdf.Array([x1, y2, x2, y2, x1, y1, x2, y1]),
                C=pikepdf.Array(color),
                Contents=pikepdf.String(ann.text),
            )
        elif ann.type == "comment":
            annot = pikepdf.Dictionary(
                Type=pikepdf.Name("/Annot"),
                Subtype=pikepdf.Name("/Text"),
                NM=nm,
                Rect=rect,
                C=pikepdf.Array(color),
                Contents=pikepdf.String(ann.text),
            )
        else:
            return  # skip unsupported types for now

        if "/Annots" not in page:
            page["/Annots"] = pikepdf.Array()
        page["/Annots"].append(pdf.make_indirect(annot))

    # ------------------------------------------------------------------
    # Sidecar JSON (fallback)
    # ------------------------------------------------------------------

    def save_json(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump([a.to_dict() for a in self._annotations], f, indent=2)

    def load_json(self, path: str) -> None:
        import os
        if not os.path.isfile(path):
            return
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self._annotations = [Annotation.from_dict(d) for d in data]


def _hex_to_pdf_color(hex_color: str) -> list:
    """Convert #RRGGBB to [r, g, b] floats 0-1."""
    h = hex_color.lstrip("#")
    if len(h) == 6:
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return [r / 255, g / 255, b / 255]
    return [1.0, 1.0, 0.0]
