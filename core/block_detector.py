"""
Détection de blocs texte dans un flux de contenu PDF.

Utilise pikepdf.parse_content_stream pour extraire les positions et contenus
de chaque opération texte (Tj, TJ) et les regroupe en lignes puis en blocs
logiques multi-lignes.

Gère les cas difficiles :
  - Flux avec /Filter cassé (écrit sans compression réelle) → read_raw_bytes()
  - Opérateurs Td (relatif), Tm (absolu), T* (newline)
  - Encodage latin-1 et UTF-16BE (hex strings)
  - TJ arrays avec ajustements kerning
"""
from __future__ import annotations

import re
import pikepdf
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class TextItem:
    """Un run texte issu d'un opérateur Tj/TJ avec sa position absolue."""
    text: str
    x: float          # coordonnée PDF (origine bas-gauche)
    y: float
    font_name: str
    font_size: float
    stream_index: int  # index dans le tableau /Contents
    bt_index: int      # numéro du bloc BT/ET (pour le déplacement)


@dataclass
class TextLine:
    """Ensemble d'items sur la même ligne horizontale (même Y ± tolérance)."""
    items: list[TextItem] = field(default_factory=list)

    @property
    def text(self) -> str:
        return " ".join(i.text for i in self.items)

    @property
    def x(self) -> float:
        return self.items[0].x if self.items else 0.0

    @property
    def y(self) -> float:
        return self.items[0].y if self.items else 0.0

    @property
    def font_size(self) -> float:
        return self.items[0].font_size if self.items else 12.0

    @property
    def font_name(self) -> str:
        return self.items[0].font_name if self.items else ""

    @property
    def x1(self) -> float:
        """Estimation du bord droit (position + largeur approx.)."""
        if not self.items:
            return self.x
        last = self.items[-1]
        return last.x + len(last.text) * last.font_size * 0.55


@dataclass
class TextBlock:
    """Bloc logique multi-lignes (paragraphe, adresse, titre…)."""
    lines: list[TextLine] = field(default_factory=list)

    @property
    def text(self) -> str:
        return "\n".join(l.text for l in self.lines)

    # Bounding box en coordonnées PDF (origine bas-gauche)
    @property
    def x0(self) -> float:
        return min(l.x for l in self.lines) if self.lines else 0.0

    @property
    def y0(self) -> float:
        """Bas du bloc — baseline moins les descendantes (~28% de la taille)."""
        return min(l.y - l.font_size * 0.28 for l in self.lines) if self.lines else 0.0

    @property
    def y1(self) -> float:
        """Haut du bloc — baseline plus les ascendantes (~85% de la taille)."""
        return max(l.y + l.font_size * 0.85 for l in self.lines) if self.lines else 0.0

    @property
    def x1(self) -> float:
        return max(l.x1 for l in self.lines) if self.lines else 0.0

    @property
    def font_size(self) -> float:
        return self.lines[0].font_size if self.lines else 12.0

    @property
    def font_name(self) -> str:
        return self.lines[0].font_name if self.lines else ""

    def norm_rect(self, page_width: float, page_height: float) -> dict:
        """Bounding box normalisée [0,1] avec y depuis le haut (comme Qt/pdfplumber)."""
        return {
            "x":      self.x0 / page_width,
            "y":      1.0 - self.y1 / page_height,
            "width":  (self.x1 - self.x0) / page_width,
            "height": (self.y1 - self.y0) / page_height,
        }


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def detect_text_blocks(
    pdf: pikepdf.Pdf,
    page_index: int,
    *,
    y_line_tol: float = 2.0,   # pt : écart Y max pour appartenir à la même ligne
    x_margin_tol: float = 8.0,  # pt : écart X max pour appartenir au même bloc
    line_spacing_factor: tuple = (0.5, 2.5),  # (min, max) * font_size pour regrouper lignes
) -> list[TextBlock]:
    """
    Parse tous les flux de contenu de la page et retourne une liste de TextBlock.

    Chaque TextBlock regroupe les lignes adjacentes (même marge gauche,
    espacement vertical cohérent avec la police) en un bloc logique.
    """
    page = pdf.pages[page_index]
    contents = page.get("/Contents")
    if contents is None:
        return []

    streams = list(contents) if isinstance(contents, pikepdf.Array) else [contents]
    all_items: list[TextItem] = []

    for si, stream_obj in enumerate(streams):
        raw = _read_stream_bytes(stream_obj)
        if raw is None:
            continue
        # Skip injection overlay streams — they should not pollute block detection
        if b'_BEGIN_PDFED' in raw:
            continue
        items = _parse_stream(pdf, stream_obj, si, raw=raw)
        all_items.extend(items)

    if not all_items:
        return []

    lines = _group_into_lines(all_items, y_tol=y_line_tol)
    blocks = _group_into_blocks(lines, x_tol=x_margin_tol,
                                 spacing_range=line_spacing_factor)
    return blocks


def get_block_at(
    pdf: pikepdf.Pdf,
    page_index: int,
    norm_x: float,
    norm_y: float,
) -> Optional[TextBlock]:
    """
    Retourne le TextBlock sous le point normalisé (norm_x, norm_y) [y depuis le haut].
    Utile pour détecter quel bloc l'utilisateur a cliqué.
    """
    page = pdf.pages[page_index]
    mb = page.get("/MediaBox", pikepdf.Array([0, 0, 595, 842]))
    pw = float(mb[2]) - float(mb[0])
    ph = float(mb[3]) - float(mb[1])

    # Convert to PDF coords (y from bottom)
    px = norm_x * pw
    py = (1.0 - norm_y) * ph

    blocks = detect_text_blocks(pdf, page_index)
    best: Optional[TextBlock] = None
    best_area = float("inf")

    for block in blocks:
        # Petite tolérance — la bbox inclut déjà ascendantes et descendantes
        tol = block.font_size * 0.3
        if (block.x0 - tol <= px <= block.x1 + tol and
                block.y0 - tol <= py <= block.y1 + tol):
            area = (block.x1 - block.x0) * (block.y1 - block.y0)
            if area < best_area:
                best = block
                best_area = area

    return best


# ---------------------------------------------------------------------------
# Stream parsing
# ---------------------------------------------------------------------------

def _read_stream_bytes(stream_obj) -> Optional[bytes]:
    """Lit le contenu d'un stream pikepdf, même si son filtre est cassé."""
    try:
        return bytes(stream_obj.read_bytes())
    except Exception:
        pass
    # Filtre déclaré mais données non encodées (bug _rewrite ancien) → lire raw
    try:
        return bytes(stream_obj.read_raw_bytes())
    except Exception:
        return None


def _parse_stream(
    pdf: pikepdf.Pdf,
    stream_obj,
    stream_index: int,
    *,
    raw: Optional[bytes] = None,
) -> list[TextItem]:
    """Parse un flux de contenu et retourne la liste des TextItem."""
    if raw is None:
        raw = _read_stream_bytes(stream_obj)
    if raw is None:
        return []

    try:
        # parse_content_stream nécessite un vrai stream pikepdf, pas des bytes bruts
        temp = pdf.make_stream(raw)
        instructions = pikepdf.parse_content_stream(temp)
    except Exception:
        return []

    items: list[TextItem] = []

    # État du texte
    cur_x: float = 0.0
    cur_y: float = 0.0
    cur_font: str = ""
    cur_font_size: float = 12.0
    in_bt: bool = False
    bt_index: int = 0
    leading: float = 0.0   # TL operator

    # CTM (current transformation matrix) — simplified: track only translation
    # Full affine would require matrix stack; here we track the [e, f] translation
    ctm_dx: float = 0.0
    ctm_dy: float = 0.0

    for instr in instructions:
        op = str(instr.operator)
        ops = instr.operands

        if op == "cm" and len(ops) == 6:
            # [a b c d e f] cm — concatenate CTM
            # For pure translations (a=1,b=0,c=0,d=1): add e,f
            try:
                a, b, c, d, e, f = (float(ops[i]) for i in range(6))
                if abs(a - 1) < 0.01 and abs(b) < 0.01 and abs(c) < 0.01 and abs(d - 1) < 0.01:
                    ctm_dx += e
                    ctm_dy += f
            except Exception:
                pass

        elif op == "q":
            pass  # push graphics state — we don't stack CTM here (simplified)

        elif op == "Q":
            ctm_dx = 0.0  # restore — simplified: reset to 0
            ctm_dy = 0.0

        elif op == "BT":
            in_bt = True
            bt_index += 1
            cur_x, cur_y = 0.0, 0.0

        elif op == "ET":
            in_bt = False

        elif not in_bt:
            continue

        elif op == "Tf" and len(ops) >= 2:
            cur_font = str(ops[0]).lstrip("/")
            try:
                cur_font_size = float(ops[1])
            except Exception:
                pass

        elif op == "TL" and len(ops) >= 1:
            try:
                leading = float(ops[0])
            except Exception:
                pass

        elif op == "Tm" and len(ops) == 6:
            # Set text matrix — e=x, f=y (absolute)
            try:
                cur_x = float(ops[4])
                cur_y = float(ops[5])
            except Exception:
                pass

        elif op == "Td" and len(ops) >= 2:
            try:
                cur_x += float(ops[0])
                cur_y += float(ops[1])
            except Exception:
                pass

        elif op == "TD" and len(ops) >= 2:
            try:
                tx, ty = float(ops[0]), float(ops[1])
                leading = -ty
                cur_x += tx
                cur_y += ty
            except Exception:
                pass

        elif op == "T*":
            cur_y -= leading if leading else cur_font_size * 1.2

        elif op in ("Tj", "'", '"'):
            if ops:
                text = _decode_string(ops[-1])  # ' and " have text as last operand
                if text.strip():
                    items.append(TextItem(
                        text=text,
                        x=cur_x + ctm_dx,
                        y=cur_y + ctm_dy,
                        font_name=cur_font,
                        font_size=cur_font_size,
                        stream_index=stream_index,
                        bt_index=bt_index,
                    ))

        elif op == "TJ" and ops:
            text = _decode_tj(ops[0])
            if text.strip():
                items.append(TextItem(
                    text=text,
                    x=cur_x + ctm_dx,
                    y=cur_y + ctm_dy,
                    font_name=cur_font,
                    font_size=cur_font_size,
                    stream_index=stream_index,
                    bt_index=bt_index,
                ))

    return items


# ---------------------------------------------------------------------------
# String decoding
# ---------------------------------------------------------------------------

def _decode_string(operand) -> str:
    """Décode un objet pikepdf.String (latin-1 ou UTF-16BE hex)."""
    try:
        raw = bytes(operand)
    except Exception:
        return str(operand)

    # UTF-16BE BOM (\xfe\xff)
    if raw.startswith(b"\xfe\xff"):
        try:
            return raw[2:].decode("utf-16-be")
        except Exception:
            pass

    # latin-1
    try:
        return raw.decode("latin-1")
    except Exception:
        return raw.decode("utf-8", errors="replace")


def _decode_tj(array_operand) -> str:
    """Décode un opérande TJ (array de strings et d'ajustements kern)."""
    parts: list[str] = []
    try:
        for item in array_operand:
            if isinstance(item, pikepdf.String):
                parts.append(_decode_string(item))
            # les nombres (kern) sont ignorés
    except Exception:
        pass
    return "".join(parts)


# ---------------------------------------------------------------------------
# Grouping
# ---------------------------------------------------------------------------

def _group_into_lines(
    items: list[TextItem],
    y_tol: float = 2.0,
    col_gap: float = 40.0,   # pt : gap X entre le bord droit d'un item et le bord gauche du suivant
) -> list[TextLine]:
    """Regroupe les TextItem en lignes (même Y ± y_tol).

    Les items séparés par un grand gap horizontal (col_gap) sont traités
    comme des colonnes distinctes et placés dans des lignes séparées.
    """
    if not items:
        return []

    # Trier : y décroissant (haut → bas), puis x croissant
    sorted_items = sorted(items, key=lambda i: (-i.y, i.x))

    lines: list[TextLine] = []
    current: list[TextItem] = [sorted_items[0]]

    for item in sorted_items[1:]:
        last = current[-1]
        same_y = abs(item.y - last.y) <= y_tol
        if same_y:
            # Vérifie si les deux items sont dans la même colonne (pas de grand gap horizontal)
            last_right = last.x + len(last.text) * last.font_size * 0.55
            x_gap = item.x - last_right
            if x_gap > col_gap:
                # Grand gap → colonne différente → nouvelle ligne
                lines.append(TextLine(items=sorted(current, key=lambda i: i.x)))
                current = [item]
            else:
                current.append(item)
        else:
            lines.append(TextLine(items=sorted(current, key=lambda i: i.x)))
            current = [item]

    if current:
        lines.append(TextLine(items=sorted(current, key=lambda i: i.x)))

    return lines


@dataclass
class InjectedBlockInfo:
    """Bloc injecté par inject_text_block (marqué _BEGIN_PDFED)."""
    block_id: str
    stream_index: int
    norm_x: float   # cover rect normalisée, y depuis le haut
    norm_y: float
    norm_w: float
    norm_h: float
    text: str = ""
    font_size: float = 12.0


def _parse_injected_stream(
    raw: bytes,
    stream_index: int,
    pw: float,
    ph: float,
) -> Optional[InjectedBlockInfo]:
    """Extrait les métadonnées d'un flux _BEGIN_PDFED."""
    try:
        content = raw.decode("latin-1")
    except Exception:
        return None

    m_id = re.search(r"% _BEGIN_PDFED (\S+)", content)
    if not m_id:
        return None
    block_id = m_id.group(1)

    # Cover rect: first "cx cy cw ch re" pattern
    m_rect = re.search(
        r"([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+re\b", content
    )
    if not m_rect:
        return None
    cx0 = float(m_rect.group(1))
    cy0 = float(m_rect.group(2))
    cw  = float(m_rect.group(3))
    ch  = float(m_rect.group(4))

    # Convert PDF coords (y from bottom) → normalized (y from top)
    norm_x = cx0 / pw
    norm_y = 1.0 - (cy0 + ch) / ph
    norm_w = cw / pw
    norm_h = ch / ph

    # Font size
    m_font = re.search(r"/\S+ ([\d.]+) Tf", content)
    font_size = float(m_font.group(1)) if m_font else 12.0

    # Text: collect all Tj strings (handle escaped parens)
    parts: list[str] = []
    for raw_str in re.findall(r"\(([^)\\]*(?:\\.[^)\\]*)*)\)\s+Tj", content):
        parts.append(
            raw_str.replace("\\(", "(").replace("\\)", ")").replace("\\\\", "\\")
        )
    text = " ".join(parts)

    return InjectedBlockInfo(
        block_id=block_id,
        stream_index=stream_index,
        norm_x=norm_x,
        norm_y=norm_y,
        norm_w=norm_w,
        norm_h=norm_h,
        text=text,
        font_size=font_size,
    )


def detect_injected_blocks(
    pdf: pikepdf.Pdf,
    page_index: int,
) -> list[InjectedBlockInfo]:
    """Retourne les blocs injectés (_BEGIN_PDFED) de la page."""
    page = pdf.pages[page_index]
    mb = page.get("/MediaBox", pikepdf.Array([0, 0, 595, 842]))
    pw = float(mb[2]) - float(mb[0])
    ph = float(mb[3]) - float(mb[1])

    contents = page.get("/Contents")
    if contents is None:
        return []
    streams = list(contents) if isinstance(contents, pikepdf.Array) else [contents]

    result: list[InjectedBlockInfo] = []
    for si, stream_obj in enumerate(streams):
        raw = _read_stream_bytes(stream_obj)
        if raw is None:
            continue
        if b"_BEGIN_PDFED" not in raw:
            continue
        info = _parse_injected_stream(raw, si, pw, ph)
        if info is not None:
            result.append(info)
    return result


def get_injected_block_at(
    pdf: pikepdf.Pdf,
    page_index: int,
    norm_x: float,
    norm_y: float,
) -> Optional[InjectedBlockInfo]:
    """Retourne le bloc injecté sous le point (norm_x, norm_y) ou None."""
    blocks = detect_injected_blocks(pdf, page_index)
    best: Optional[InjectedBlockInfo] = None
    best_area = float("inf")
    for b in blocks:
        tol = b.norm_w * 0.05  # 5% tolerance
        if (b.norm_x - tol <= norm_x <= b.norm_x + b.norm_w + tol and
                b.norm_y - tol <= norm_y <= b.norm_y + b.norm_h + tol):
            area = b.norm_w * b.norm_h
            if area < best_area:
                best = b
                best_area = area
    return best


def _group_into_blocks(
    lines: list[TextLine],
    x_tol: float = 8.0,
    spacing_range: tuple = (0.5, 2.5),
) -> list[TextBlock]:
    """
    Regroupe les TextLine en TextBlock logiques.

    Critères de regroupement :
      1. Même marge gauche (x0) à x_tol près
      2. Espacement vertical dy cohérent : spacing_range[0]*fs ≤ dy ≤ spacing_range[1]*fs
    """
    if not lines:
        return []

    blocks: list[TextBlock] = []
    current: list[TextLine] = [lines[0]]

    for line in lines[1:]:
        prev = current[-1]
        dy = prev.y - line.y                      # positif = descente
        expected_fs = prev.font_size
        min_dy = spacing_range[0] * expected_fs
        max_dy = spacing_range[1] * expected_fs

        same_margin = abs(line.x - current[0].x) <= x_tol
        good_spacing = min_dy <= dy <= max_dy
        same_font_size = abs(line.font_size - prev.font_size) < 1.0

        if same_margin and good_spacing and same_font_size:
            current.append(line)
        else:
            blocks.append(TextBlock(lines=current))
            current = [line]

    if current:
        blocks.append(TextBlock(lines=current))

    return blocks
