"""
In-place PDF text editor.
Modifies content streams directly so the PDF viewer renders the replacement text
with the same embedded font glyphs → pixel-perfect stroke thickness.

Falls back gracefully to overlay annotation when the encoding is too complex.
"""
from __future__ import annotations

import re
from io import BytesIO
from typing import Optional, Tuple

import pikepdf


# ------------------------------------------------------------------
# Public result codes
# ------------------------------------------------------------------

class Method:
    LITERAL  = "inplace_literal"   # (text) Tj — direct bytes
    HEX_UTF16 = "inplace_hex_utf16" # <HEXHEX> Tj — UTF-16BE
    TJ_ARRAY  = "inplace_tj_array"  # [(text) kern] TJ
    FALLBACK  = "overlay_fallback"  # could not modify stream


# ------------------------------------------------------------------
# Entry point
# ------------------------------------------------------------------

def replace_text_inplace(
    pdf: pikepdf.Pdf,
    page_index: int,
    old_text: str,
    new_text: str,
    *,
    stream_index: Optional[int] = None,
    bt_index: Optional[int] = None,
) -> Tuple[bool, str]:
    """
    Attempt to replace *old_text* with *new_text* in the PDF content stream
    of the given page.

    If *stream_index* and *bt_index* are provided (from block_detector), the
    replacement targets only that specific BT block, so duplicate text strings
    in other positions are not accidentally modified.

    Returns (success, method_name).
    On failure the caller should fall back to an overlay annotation.
    """
    try:
        page = pdf.pages[page_index]
        contents = page.get("/Contents")
        if contents is None:
            return False, Method.FALLBACK

        streams = list(contents) if isinstance(contents, pikepdf.Array) else [contents]

        # Targeted replacement: specific stream + BT block
        if stream_index is not None and bt_index is not None:
            if stream_index < len(streams):
                ok, method = _replace_in_bt_block(
                    pdf, streams[stream_index], bt_index, old_text, new_text
                )
                if ok:
                    return True, method
            # Fall through to untargeted replacement if targeted failed
            # (e.g. encoding mismatch caught by BT-level parser)

        for stream_obj in streams:
            ok, method = _replace_in_stream(stream_obj, old_text, new_text)
            if ok:
                return True, method

        return False, Method.FALLBACK

    except Exception:
        return False, Method.FALLBACK


def _replace_in_bt_block(
    pdf: pikepdf.Pdf,
    stream_obj,
    target_bt_index: int,
    old_text: str,
    new_text: str,
) -> Tuple[bool, str]:
    """
    Replace *old_text* with *new_text* only inside the BT block identified by
    *target_bt_index* (1-based, as counted by block_detector).

    Uses parse_content_stream so it is position-exact regardless of how many
    identical strings exist elsewhere in the stream.
    """
    from core.block_detector import _read_stream_bytes
    raw = _read_stream_bytes(stream_obj)
    if raw is None:
        return False, Method.FALLBACK

    try:
        temp = pdf.make_stream(raw)
        instructions = list(pikepdf.parse_content_stream(temp))
    except Exception:
        return False, Method.FALLBACK

    bt_count = 0
    in_target = False
    new_instructions = []
    replaced = False

    for instr in instructions:
        op = str(instr.operator)
        if op == "BT":
            bt_count += 1
            in_target = (bt_count == target_bt_index)
            new_instructions.append(instr)
        elif op == "ET":
            in_target = False
            new_instructions.append(instr)
        elif in_target and not replaced:
            result, method = _replace_in_instruction(instr, old_text, new_text, pdf)
            new_instructions.append(result)
            if result is not instr:
                replaced = True
                # Keep track of the method used
                _replace_in_bt_block._last_method = method
        else:
            new_instructions.append(instr)

    if not replaced:
        return False, Method.FALLBACK

    try:
        new_bytes = pikepdf.unparse_content_stream(new_instructions)
        stream_write_compressed(stream_obj, new_bytes)
        method = getattr(_replace_in_bt_block, '_last_method', Method.LITERAL)
        return True, method
    except Exception:
        return False, Method.FALLBACK


def _replace_in_instruction(instr, old_text: str, new_text: str, pdf) -> Tuple[object, str]:
    """
    Try to replace *old_text* in a single content stream instruction.
    Returns (new_instr_or_original, method).  If no replacement was made,
    returns the original instruction unchanged.
    """
    from core.text_mover import _parse_single

    op = str(instr.operator)

    # Tj / ' / " — single string operand
    if op in ("Tj", "'", '"') and instr.operands:
        operand = instr.operands[-1]
        decoded = _decode_operand(operand)
        if old_text not in decoded:
            return instr, Method.FALLBACK
        replaced = decoded.replace(old_text, new_text, 1)
        # Re-encode as literal string
        raw_instr = f"({_pdf_escape(replaced)}) {op}\n".encode("latin-1", errors="replace")
        new_instr = _parse_single(raw_instr, pdf)
        if new_instr is not None:
            return new_instr, Method.LITERAL
        return instr, Method.FALLBACK

    # TJ — array of strings and kern adjustments
    if op == "TJ" and instr.operands:
        arr = instr.operands[0]
        parts = []
        full = ""
        for item in arr:
            if isinstance(item, pikepdf.String):
                decoded = _decode_operand(item)
                parts.append(("str", decoded))
                full += decoded
            else:
                parts.append(("num", item))

        if old_text not in full:
            return instr, Method.FALLBACK

        # Simple case: replace within a single string part
        for i, (kind, val) in enumerate(parts):
            if kind == "str" and old_text in val:
                parts[i] = ("str", val.replace(old_text, new_text, 1))
                break
        else:
            # Cross-part replacement: collapse → replace → emit as Tj
            new_full = full.replace(old_text, new_text, 1)
            raw_instr = f"({_pdf_escape(new_full)}) Tj\n".encode("latin-1", errors="replace")
            new_instr = _parse_single(raw_instr, pdf)
            return (new_instr if new_instr is not None else instr), Method.TJ_ARRAY

        # Rebuild TJ array
        items_str = " ".join(
            f"({_pdf_escape(v)})" if kind == "str" else str(float(v))
            for kind, v in parts
        )
        raw_instr = f"[{items_str}] TJ\n".encode("latin-1", errors="replace")
        new_instr = _parse_single(raw_instr, pdf)
        if new_instr is not None:
            return new_instr, Method.TJ_ARRAY
        return instr, Method.FALLBACK

    return instr, Method.FALLBACK


def _decode_operand(operand) -> str:
    """Decode a pikepdf string operand (latin-1 or UTF-16BE)."""
    try:
        raw = bytes(operand)
    except Exception:
        return str(operand)
    if raw.startswith(b"\xfe\xff"):
        try:
            return raw[2:].decode("utf-16-be")
        except Exception:
            pass
    try:
        return raw.decode("latin-1")
    except Exception:
        return raw.decode("utf-8", errors="replace")


# ------------------------------------------------------------------
# Per-stream replacement
# ------------------------------------------------------------------

def _replace_in_stream(stream_obj, old_text: str, new_text: str) -> Tuple[bool, str]:
    """Try all strategies on a single pikepdf stream object."""

    # Read and decompress (pikepdf does this automatically)
    raw = stream_obj.read_bytes()
    try:
        content = raw.decode("latin-1")
    except Exception:
        content = raw.decode("utf-8", errors="replace")

    # ---- Strategy 1: literal string  (text) Tj -------------------------
    escaped = re.escape(old_text)
    pattern = r'\(' + escaped + r'\)'
    if re.search(pattern, content):
        new_content = re.sub(
            pattern,
            '(' + _pdf_escape(new_text) + ')',
            content, count=1,
        )
        if new_content != content:
            _rewrite(stream_obj, new_content)
            return True, Method.LITERAL

    # ---- Strategy 2: hex UTF-16BE  <HEXHEX> Tj -------------------------
    old_hex = old_text.encode("utf-16-be").hex().upper()
    if re.search(r'<' + re.escape(old_hex) + r'>', content, re.IGNORECASE):
        new_hex = new_text.encode("utf-16-be").hex().upper()
        new_content = re.sub(
            r'<' + re.escape(old_hex) + r'>',
            '<' + new_hex + '>',
            content, count=1, flags=re.IGNORECASE,
        )
        if new_content != content:
            _rewrite(stream_obj, new_content)
            return True, Method.HEX_UTF16

    # ---- Strategy 3: TJ array  [(str) kern (str)] TJ -------------------
    ok, new_content = _replace_tj(content, old_text, new_text)
    if ok:
        _rewrite(stream_obj, new_content)
        return True, Method.TJ_ARRAY

    return False, Method.FALLBACK


# ------------------------------------------------------------------
# TJ array replacement
# ------------------------------------------------------------------

_TJ_RE = re.compile(r'\[([^\]]*)\]\s*TJ', re.DOTALL)
_STR_RE = re.compile(r'\(([^)\\]*(?:\\.[^)\\]*)*)\)')  # handles \" etc.


def _replace_tj(content: str, old_text: str, new_text: str) -> Tuple[bool, str]:
    """Replace old_text inside TJ array operators."""
    replaced = [False]

    def _sub(m: re.Match) -> str:
        if replaced[0]:
            return m.group(0)
        inner = m.group(1)

        # Reconstruct the concatenated string from all literal parts
        parts = _STR_RE.findall(inner)
        full = "".join(_pdf_unescape(p) for p in parts)

        if old_text not in full:
            return m.group(0)

        # Simple case: old_text matches exactly one part
        for i, raw_part in enumerate(parts):
            decoded = _pdf_unescape(raw_part)
            if decoded == old_text:
                new_inner = inner.replace(
                    '(' + raw_part + ')',
                    '(' + _pdf_escape(new_text) + ')',
                    1,
                )
                replaced[0] = True
                return '[' + new_inner + '] TJ'

        # Fallback: collapse all parts, replace, emit as single Tj
        new_full = full.replace(old_text, new_text, 1)
        if new_full != full:
            replaced[0] = True
            return '(' + _pdf_escape(new_full) + ') Tj'

        return m.group(0)

    new_content = _TJ_RE.sub(_sub, content)
    return replaced[0], new_content


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _pdf_escape(s: str) -> str:
    """Escape a string for use inside PDF parenthesised string literals."""
    return (s
            .replace("\\", "\\\\")
            .replace("(", "\\(")
            .replace(")", "\\)")
            .replace("\r", "\\r")
            .replace("\n", "\\n"))


def _pdf_unescape(s: str) -> str:
    """Reverse basic PDF string escaping."""
    return (s
            .replace("\\\\", "\\")
            .replace("\\(", "(")
            .replace("\\)", ")")
            .replace("\\r", "\r")
            .replace("\\n", "\n"))


def _rewrite(stream_obj, content: str) -> None:
    """Write modified content back with proper FlateDecode compression.

    pikepdf.write(data, filter=FlateDecode) does NOT compress — it only
    sets the /Filter key while storing raw bytes, making the stream
    unreadable by pikepdf on subsequent calls (inflate error).
    We must compress explicitly with zlib before writing.
    """
    stream_write_compressed(stream_obj, content.encode("latin-1"))


def stream_write_compressed(stream_obj, data: bytes) -> None:
    """Write bytes to a pikepdf stream with proper FlateDecode compression.

    This is the correct way to write a compressed stream in pikepdf:
      - zlib.compress() produces RFC-1950 (zlib/deflate) output
      - Passing it with filter=FlateDecode tells pikepdf the bytes are
        already encoded in FlateDecode format
      - pikepdf's read_bytes() then successfully decompresses on the next read
    """
    import zlib
    compressed = zlib.compress(data, level=6)
    stream_obj.write(compressed, filter=pikepdf.Name("/FlateDecode"))


def stream_write_raw(stream_obj, data: bytes) -> None:
    """Write bytes as uncompressed (no /Filter) stream.
    Larger on disk but always readable by pikepdf and all PDF renderers.
    """
    stream_obj.write(data)
