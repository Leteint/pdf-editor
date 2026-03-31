"""
Injection directe de blocs texte dans le flux de contenu PDF.

Chaque bloc est encadré de marqueurs commentaire :
    % _BEGIN_PDFED <block_id>
    ...
    % _END_PDFED <block_id>

Cela permet la suppression/remplacement ciblé des blocs injectés.
"""
from __future__ import annotations

import pikepdf

# Standard PDF Type1 fonts — always available, no embedding required
_STD_FONTS: dict[str, dict] = {
    "helvetica": {
        (False, False): "Helvetica",
        (True,  False): "Helvetica-Bold",
        (False, True):  "Helvetica-Oblique",
        (True,  True):  "Helvetica-BoldOblique",
    },
    "times": {
        (False, False): "Times-Roman",
        (True,  False): "Times-Bold",
        (False, True):  "Times-Italic",
        (True,  True):  "Times-BoldItalic",
    },
    "courier": {
        (False, False): "Courier",
        (True,  False): "Courier-Bold",
        (False, True):  "Courier-Oblique",
        (True,  True):  "Courier-BoldOblique",
    },
}

# Map common family names to the standard PDF family key
_FAMILY_ALIASES: dict[str, str] = {
    "arial":            "helvetica",
    "helvetica":        "helvetica",
    "helvetica neue":   "helvetica",
    "verdana":          "helvetica",
    "tahoma":           "helvetica",
    "calibri":          "helvetica",
    "trebuchet ms":     "helvetica",
    "gill sans":        "helvetica",
    "times new roman":  "times",
    "times":            "times",
    "georgia":          "times",
    "palatino":         "times",
    "garamond":         "times",
    "courier new":      "courier",
    "courier":          "courier",
    "lucida console":   "courier",
    "consolas":         "courier",
}

# Keep for backwards compatibility
_FONT_MAP = {
    (False, False): ("Helvetica",             "Helvetica"),
    (True,  False): ("Helvetica-Bold",        "Helvetica-Bold"),
    (False, True):  ("Helvetica-Oblique",     "Helvetica-Oblique"),
    (True,  True):  ("Helvetica-BoldOblique", "Helvetica-BoldOblique"),
}


def _resolve_font(family: str, bold: bool, italic: bool) -> str:
    """Return the standard PDF BaseFont name for the given family + style."""
    key = _FAMILY_ALIASES.get(family.lower().strip(), "helvetica")
    variants = _STD_FONTS.get(key, _STD_FONTS["helvetica"])
    return variants[(bold, italic)]


def _font_resource_key(base_font: str) -> str:
    """Turn 'Helvetica-Bold' → 'F_HelvBold' (safe PDF name, no spaces)."""
    return "F_" + base_font.replace("-", "").replace(" ", "")[:16]


def _ensure_page_font(pdf: pikepdf.Pdf, page: pikepdf.Object,
                      font_key: str, base_font: str) -> None:
    if "/Resources" not in page:
        page["/Resources"] = pikepdf.Dictionary()
    res = page["/Resources"]
    if "/Font" not in res:
        res["/Font"] = pikepdf.Dictionary()
    if f"/{font_key}" not in res["/Font"]:
        res["/Font"][f"/{font_key}"] = pdf.make_indirect(pikepdf.Dictionary(
            Type=pikepdf.Name.Font,
            Subtype=pikepdf.Name.Type1,
            BaseFont=pikepdf.Name(f"/{base_font}"),
            Encoding=pikepdf.Name.WinAnsiEncoding,
        ))


def _color_op(color_hex: str) -> str:
    try:
        h = color_hex.lstrip("#")
        r, g, b = int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255
        return f"{r:.4f} {g:.4f} {b:.4f} rg"
    except Exception:
        return "0 g"


def _encode(text: str) -> str:
    try:
        s = text.encode("latin-1").decode("latin-1")
    except UnicodeEncodeError:
        s = text.encode("ascii", errors="replace").decode("ascii")
    return s.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _append_stream(pdf: pikepdf.Pdf, page: pikepdf.Object, data: bytes) -> None:
    """Ajoute un nouveau flux indépendant — ne modifie jamais le flux original
    pour éviter l'erreur inflate (filter /FlateDecode non nettoyé par write())."""
    new_stream = pdf.make_indirect(pdf.make_stream(data))
    contents = page.get("/Contents")
    if contents is None:
        page["/Contents"] = new_stream
    elif isinstance(contents, pikepdf.Array):
        contents.append(new_stream)
    else:
        # Flux unique → convertir en tableau [original, nouveau]
        page["/Contents"] = pikepdf.Array([contents, new_stream])


def _build_block_bytes(
    block_id: str,
    pw: float, ph: float,
    cover_nx: float, cover_ny: float, cover_nw: float, cover_nh: float,
    text_nx: float, text_ny: float, text_nw: float, text_nh: float,
    text: str,
    font_size: float,
    bold: bool,
    italic: bool,
    color: str,
    letter_spacing: float,
    font_family: str = "Helvetica",
    bg_color: str = "",
) -> bytes:
    """Construit les bytes du bloc d'injection (sans toucher au PDF)."""
    cx0 = cover_nx * pw
    cy0 = (1.0 - cover_ny - cover_nh) * ph
    cw  = cover_nw * pw
    ch  = cover_nh * ph

    tx0 = text_nx * pw
    ty0 = (1.0 - text_ny - text_nh) * ph
    tw  = text_nw * pw

    base_font = _resolve_font(font_family, bold, italic)
    font_key  = _font_resource_key(base_font)

    char_w = font_size * 0.55
    max_lw = max(char_w, tw - 4.0)
    wrapped: list[str] = []
    cur = ""
    for word in text.split(" "):
        candidate = f"{cur} {word}".strip() if cur else word
        if len(candidate) * char_w <= max_lw:
            cur = candidate
        else:
            if cur:
                wrapped.append(cur)
            cur = word
    if cur:
        wrapped.append(cur)
    if not wrapped:
        wrapped = [""]

    line_h = font_size * 1.4
    baseline_y = ty0 + font_size * 0.25
    col = _color_op(color)
    tc = f"{letter_spacing:.4f} Tc\n" if letter_spacing > 0 else ""

    # Fond coloré : deux rects séparés.
    #   1. Rect blanc pleine hauteur (cover_nh) → masque le texte original dessous.
    #   2. Rect coloré serré autour du texte → évite de cacher le contenu adjacent.
    # Si bg_color vide → aucun rect (texte flotte sur le fond original).
    _bg = bg_color.strip() if bg_color else ""
    if _bg:
        # Rect coloré serré autour du texte — masque le texte original ET fournit le fond visuel.
        # Pas de rect blanc supplémentaire : il effacerait le contenu adjacent.
        tight_bottom = baseline_y - font_size * 0.28
        tight_h      = font_size * 1.15
        cover_part = (
            f"q\n{_color_op(_bg)}\n{cx0:.3f} {tight_bottom:.3f} {cw:.3f} {tight_h:.3f} re\nf\nQ\n"
        )
    else:
        cover_part = ""

    parts: list[str] = [
        f"% _BEGIN_PDFED {block_id}\n",
        cover_part,
        f"q\nBT\n/{font_key} {font_size:.2f} Tf\n{col}\n{tc}",
    ]
    y = baseline_y
    for i, line in enumerate(wrapped):
        safe = _encode(line)
        if i == 0:
            parts.append(f"{tx0 + 2:.3f} {y:.3f} Td\n")
        else:
            y -= line_h
            parts.append(f"0 {-line_h:.3f} Td\n")
        parts.append(f"({safe}) Tj\n")
    parts += ["ET\nQ\n", f"% _END_PDFED {block_id}\n"]

    return "".join(parts).encode("latin-1")


def _find_and_overwrite_stream(
    page: pikepdf.Object,
    block_id: str,
    new_data: bytes,
) -> bool:
    """Cherche le flux contenant block_id et l'écrase avec new_data.
    Retourne True si trouvé et écrasé."""
    contents = page.get("/Contents")
    if contents is None:
        return False

    begin = f"% _BEGIN_PDFED {block_id}\n".encode()

    if isinstance(contents, pikepdf.Array):
        for i in range(len(contents) - 1, -1, -1):
            stream = contents[i]
            try:
                raw = bytes(stream.read_bytes())
            except Exception:
                continue
            if begin in raw:
                stream.write(new_data)
                return True
    else:
        try:
            raw = bytes(contents.read_bytes())
        except Exception:
            return False
        if begin in raw:
            contents.write(new_data)
            return True

    return False


def inject_text_block(
    pdf: pikepdf.Pdf,
    page_index: int,
    block_id: str,
    # rectangle de couverture (normalized, y depuis le haut)
    cover_nx: float, cover_ny: float, cover_nw: float, cover_nh: float,
    # rectangle de texte (normalized, y depuis le haut)
    text_nx: float, text_ny: float, text_nw: float, text_nh: float,
    text: str,
    font_size: float = 12.0,
    bold: bool = False,
    italic: bool = False,
    color: str = "#000000",
    letter_spacing: float = 0.0,
    font_family: str = "Helvetica",
    bg_color: str = "",
    replace_block_id: str = "",
) -> bool:
    """
    Injecte un bloc texte (fond blanc + texte) dans le flux de contenu de la page.

    Si replace_block_id est fourni, cherche le flux existant contenant ce bloc
    et l'écrase en place (évite les flux fantômes). Sinon, ajoute un nouveau flux.

    Retourne True si succès.
    """
    try:
        page = pdf.pages[page_index]
        mb = page.get("/MediaBox", pikepdf.Array([0, 0, 595, 842]))
        pw = float(mb[2]) - float(mb[0])
        ph = float(mb[3]) - float(mb[1])

        base_font = _resolve_font(font_family, bold, italic)
        font_key  = _font_resource_key(base_font)
        _ensure_page_font(pdf, page, font_key, base_font)

        new_data = _build_block_bytes(
            block_id, pw, ph,
            cover_nx, cover_ny, cover_nw, cover_nh,
            text_nx, text_ny, text_nw, text_nh,
            text, font_size, bold, italic, color, letter_spacing,
            font_family=font_family, bg_color=bg_color,
        )

        if replace_block_id:
            # Écraser le flux existant en place — pas de flux fantôme
            if _find_and_overwrite_stream(page, replace_block_id, new_data):
                return True
            # Flux non trouvé (ex: première injection échouée) → ajouter normalement

        _append_stream(pdf, page, new_data)
        return True

    except Exception as exc:
        print(f"[inject_text_block] {exc}")
        return False


def delete_native_text_block(
    pdf: pikepdf.Pdf,
    page_index: int,
    block,  # TextBlock from block_detector — duck-typed to avoid circular import
) -> bool:
    """
    Supprime un bloc texte natif directement du flux de contenu PDF.

    Contrairement à un rectangle blanc (non-destructif), cette fonction
    modifie le stream source pour retirer les opérateurs BT/ET identifiés,
    rendant le texte inaccessible aux extracteurs, moteurs de recherche, etc.

    Retourne True si au moins un bloc a été supprimé.
    """
    # Collect (stream_index → set of bt_indices) from all TextItems in the block
    targets: dict[int, set] = {}
    try:
        for line in block.lines:
            for item in line.items:
                targets.setdefault(item.stream_index, set()).add(item.bt_index)
    except Exception as exc:
        print(f"[delete_native_text_block] block traversal: {exc}")
        return False

    if not targets:
        return False

    page = pdf.pages[page_index]
    contents = page.get("/Contents")
    if contents is None:
        return False

    streams = list(contents) if isinstance(contents, pikepdf.Array) else [contents]
    modified = False

    for si, bt_indices_to_remove in targets.items():
        if si >= len(streams):
            continue
        stream_obj = streams[si]

        # Read stream bytes (handle broken FlateDecode filters)
        raw: bytes | None = None
        try:
            raw = bytes(stream_obj.read_bytes())
        except Exception:
            try:
                raw = bytes(stream_obj.read_raw_bytes())
            except Exception:
                continue
        if raw is None:
            continue

        # Skip injection overlay streams — should never happen but be safe
        if b"_BEGIN_PDFED" in raw:
            continue

        try:
            temp = pdf.make_stream(raw)
            instructions = pikepdf.parse_content_stream(temp)
        except Exception as exc:
            print(f"[delete_native_text_block] parse error stream {si}: {exc}")
            continue

        # Walk instructions, dropping BT/ET blocks whose bt_index is targeted
        result: list = []
        current_bt_index = 0
        in_target_bt = False

        for instr in instructions:
            op = str(instr.operator)

            if op == "BT":
                current_bt_index += 1
                if current_bt_index in bt_indices_to_remove:
                    in_target_bt = True
                    continue          # drop the BT itself
                in_target_bt = False

            if in_target_bt:
                if op == "ET":
                    in_target_bt = False
                continue              # drop everything inside + the ET

            result.append(instr)

        if len(result) < len(instructions):
            try:
                new_data = pikepdf.unparse_content_stream(result)
                stream_obj.write(new_data if new_data.strip() else b"q Q\n")
                modified = True
            except Exception as exc:
                print(f"[delete_native_text_block] write error stream {si}: {exc}")

    return modified


def inject_invisible_text_layer(
    pdf: pikepdf.Pdf,
    page_index: int,
    lines: list,
) -> bool:
    """Injecte une couche texte invisible (Tr 3) dans le flux de contenu de la page.

    Chaque entrée de `lines` doit contenir :
        text     : str   — texte à rendre cherchable
        norm_x   : float — position gauche normalisée (0-1)
        norm_y   : float — position haute normalisée (0-1)
        norm_h   : float — hauteur normalisée
        font_size: float — taille de police en points

    Tr 3 = mode invisible : le texte ne s'affiche pas mais est indexable,
    extractible (copier-coller) et accessible via Ctrl+F dans les lecteurs PDF.
    """
    if not lines:
        return False

    page = pdf.pages[page_index]
    mb = page.get("/MediaBox", pikepdf.Array([0, 0, 595, 842]))
    pw = float(mb[2]) - float(mb[0])
    ph = float(mb[3]) - float(mb[1])

    _ensure_page_font(pdf, page, "F_Helvetica", "Helvetica")

    parts: list[str] = ["% _BEGIN_PDFED_OCR_LAYER\n"]
    for line in lines:
        text = (line.get("text") or "").strip()
        if not text:
            continue
        nx = float(line.get("norm_x", 0.0))
        ny = float(line.get("norm_y", 0.0))
        nh = float(line.get("norm_h", 0.02))
        fs = float(line.get("font_size", 10.0))
        x = nx * pw
        y = (1.0 - ny - nh) * ph + fs * 0.25   # baseline
        safe = _encode(text)
        parts.append(
            f"q\nBT\n3 Tr\n/F_Helvetica {fs:.2f} Tf\n"
            f"{x:.3f} {y:.3f} Td\n({safe}) Tj\nET\nQ\n"
        )
    parts.append("% _END_PDFED_OCR_LAYER\n")

    stream_bytes = "".join(parts).encode("latin-1")
    new_stream = pdf.make_indirect(pikepdf.Stream(pdf, stream_bytes))

    contents = page.get("/Contents")
    if contents is None:
        page["/Contents"] = new_stream
    elif isinstance(contents, pikepdf.Array):
        contents.append(new_stream)
    else:
        page["/Contents"] = pikepdf.Array([contents, new_stream])

    return True


def remove_injected_block(
    pdf: pikepdf.Pdf,
    page_index: int,
    block_id: str,
) -> bool:
    """Supprime un bloc précédemment injecté par inject_text_block."""
    try:
        page = pdf.pages[page_index]
        contents = page.get("/Contents")
        if contents is None:
            return False

        begin = f"% _BEGIN_PDFED {block_id}\n".encode()
        end   = f"% _END_PDFED {block_id}\n".encode()

        def _strip(data: bytes) -> bytes:
            bi = data.find(begin)
            if bi < 0:
                return data
            ei = data.find(end, bi)
            if ei < 0:
                return data
            return data[:bi] + data[ei + len(end):]

        if isinstance(contents, pikepdf.Array):
            for i in range(len(contents) - 1, -1, -1):
                stream = contents[i]
                try:
                    raw = bytes(stream.read_bytes())
                except Exception:
                    continue
                cleaned = _strip(raw)
                if cleaned != raw:
                    stream.write(cleaned if cleaned.strip() else b"q Q\n")
                    return True
        else:
            raw = bytes(contents.read_bytes())
            cleaned = _strip(raw)
            if cleaned != raw:
                contents.write(cleaned)
                return True
        return False

    except Exception as exc:
        print(f"[remove_injected_block] {exc}")
        return False
