"""
Internationalisation (i18n) — simple dictionary-based translation.

Usage (in every UI module):
    from utils.i18n import _

Usage (once at startup, before any UI is built):
    from utils.i18n import set_language
    set_language("en")

French strings are the canonical keys.  When the current language is "fr"
the identity function is used so no dictionary lookup is needed.

Adding a new language:
    1. Create  assets/translations/<code>.py  with a TRANSLATIONS dict.
    2. Add the code + display name to SUPPORTED_LANGUAGES below.
"""
from __future__ import annotations

import importlib

_translations: dict[str, str] = {}
_current_lang: str = "fr"

# Ordered dict preserves insertion order → menu appears in this order.
SUPPORTED_LANGUAGES: dict[str, str] = {
    "fr": "Français",
    "en": "English",
    "de": "Deutsch",
    "es": "Español",
    "it": "Italiano",
    "pt": "Português",
    "ru": "Русский",
}


def set_language(lang: str) -> None:
    """Load the translation table for *lang* (call once at startup)."""
    global _translations, _current_lang
    if lang not in SUPPORTED_LANGUAGES:
        lang = "fr"
    _current_lang = lang
    if lang == "fr":
        _translations = {}   # identity — no lookup needed
        return
    try:
        mod = importlib.import_module(f"assets.translations.{lang}")
        _translations = dict(mod.TRANSLATIONS)
    except Exception:
        _translations = {}


def get_language() -> str:
    return _current_lang


def _(s: str) -> str:
    """Return the translation of *s* for the active language, or *s* itself."""
    return _translations.get(s, s)
