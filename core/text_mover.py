"""
Déplacement d'un bloc texte directement dans le flux de contenu PDF.

Stratégie :
  1. Parser le flux avec parse_content_stream → liste d'instructions
  2. Identifier les blocs BT/ET cibles (par stream_index + bt_index)
  3. Modifier les opérateurs de position (Tm/Td) dans chaque BT cible
  4. Insérer un rectangle blanc sur la bbox originale avant le 1er BT modifié
  5. Reconstruire avec unparse_content_stream et écrire avec FlateDecode

Avantages vs overlay injection :
  - Préserve la police et la taille d'origine (pas de fallback Helvetica)
  - Un seul stream modifié, pas d'accumulation de streams fantômes

Limites :
  - CTM complexes (rotations, echelles) : le déplacement peut être imprécis
"""
from __future__ import annotations

import pikepdf
from typing import Optional

from core.block_detector import TextBlock, _read_stream_bytes
from core.text_editor import stream_write_compressed


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def move_text_block(
    pdf: pikepdf.Pdf,
    page_index: int,
    block: TextBlock,
    new_norm_x: float,
    new_norm_y: float,   # y depuis le haut (coordonnées normalisées Qt)
) -> bool:
    """
    Déplace un TextBlock vers (new_norm_x, new_norm_y).
    Retourne True si au moins un stream a été modifié avec succès.
    """
    try:
        page = pdf.pages[page_index]
        mb = page.get("/MediaBox", pikepdf.Array([0, 0, 595, 842]))
        pw = float(mb[2]) - float(mb[0])
        ph = float(mb[3]) - float(mb[1])

        # Offset en coordonnées PDF (origine bas-gauche)
        new_x_pdf = new_norm_x * pw
        new_y1_pdf = (1.0 - new_norm_y) * ph   # haut du bloc

        dx = new_x_pdf - block.x0
        dy = new_y1_pdf - block.y1

        contents = page.get("/Contents")
        if contents is None:
            return False

        streams = list(contents) if isinstance(contents, pikepdf.Array) else [contents]

        # bt_index cibles par stream
        targets: dict[int, set[int]] = {}
        for line in block.lines:
            for item in line.items:
                targets.setdefault(item.stream_index, set()).add(item.bt_index)

        any_moved = False

        for si, stream_obj in enumerate(streams):
            if si not in targets:
                continue

            raw = _read_stream_bytes(stream_obj)
            if raw is None:
                continue

            try:
                temp = pdf.make_stream(raw)
                instructions = list(pikepdf.parse_content_stream(temp))
            except Exception as e:
                print(f"[text_mover] parse stream {si}: {e}")
                continue

            new_instructions = _apply_move(
                instructions, targets[si], dx, dy, block, pdf
            )

            try:
                new_bytes = pikepdf.unparse_content_stream(new_instructions)
                stream_write_compressed(stream_obj, new_bytes)
                any_moved = True
            except Exception as e:
                print(f"[text_mover] write stream {si}: {e}")

        return any_moved

    except Exception as exc:
        import traceback
        print(f"[move_text_block] {exc}")
        traceback.print_exc()
        return False


# ---------------------------------------------------------------------------
# Core: modify instruction list
# ---------------------------------------------------------------------------

def _apply_move(
    instructions: list,
    bt_set: set[int],
    dx: float,
    dy: float,
    block: TextBlock,
    pdf: pikepdf.Pdf,
) -> list:
    """
    Parcourt les instructions et modifie Tm/Td dans les BT cibles.

    Pas de rectangle blanc : le texte est déplacé directement dans le stream,
    donc l'ancienne position est vide mécaniquement — rien à masquer.
    """
    result: list = []
    in_bt = False
    bt_index = 0
    first_pos_done = False

    for instr in instructions:
        op = str(instr.operator)

        if op == "BT":
            in_bt = True
            bt_index += 1
            first_pos_done = False
            result.append(instr)

        elif op == "ET":
            in_bt = False
            result.append(instr)

        elif in_bt and bt_index in bt_set and not first_pos_done:
            if op == "Tm" and len(instr.operands) == 6:
                shifted = _shift_tm(instr, dx, dy, pdf)
                result.append(shifted if shifted is not None else instr)
                first_pos_done = True

            elif op in ("Td", "TD") and len(instr.operands) >= 2:
                shifted = _shift_td(instr, dx, dy, pdf)
                result.append(shifted if shifted is not None else instr)
                first_pos_done = True

            else:
                result.append(instr)

        else:
            result.append(instr)

    return result


# ---------------------------------------------------------------------------
# Instruction builders (via parse_content_stream on temp streams)
# ---------------------------------------------------------------------------

def _parse_single(raw: bytes, pdf: pikepdf.Pdf) -> Optional[object]:
    """Parse une instruction depuis des bytes bruts, dans le contexte d'un PDF."""
    try:
        instrs = pikepdf.parse_content_stream(pdf.make_stream(raw))
        return instrs[0] if instrs else None
    except Exception as e:
        print(f"[_parse_single] {e} — raw={repr(raw[:40])}")
        return None


def _shift_tm(instr, dx: float, dy: float, pdf: pikepdf.Pdf) -> Optional[object]:
    """Crée un Tm décalé de (dx, dy) sur les composantes de translation e,f."""
    try:
        a = float(instr.operands[0])
        b = float(instr.operands[1])
        c = float(instr.operands[2])
        d = float(instr.operands[3])
        e = float(instr.operands[4]) + dx
        f = float(instr.operands[5]) + dy
        raw = f"{a:.6f} {b:.6f} {c:.6f} {d:.6f} {e:.6f} {f:.6f} Tm\n".encode()
        return _parse_single(raw, pdf)
    except Exception as exc:
        print(f"[_shift_tm] {exc}")
        return None


def _shift_td(instr, dx: float, dy: float, pdf: pikepdf.Pdf) -> Optional[object]:
    """Crée un Td/TD décalé de (dx, dy)."""
    try:
        op = str(instr.operator)
        tx = float(instr.operands[0]) + dx
        ty = float(instr.operands[1]) + dy
        raw = f"{tx:.6f} {ty:.6f} {op}\n".encode()
        return _parse_single(raw, pdf)
    except Exception as exc:
        print(f"[_shift_td] {exc}")
        return None


