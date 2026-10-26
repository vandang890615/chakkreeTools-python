# SPDX-License-Identifier: MIT
# Copyright (C) 2026 Chakkree Tiyawongsuwan, PRIDA-TAKON and contributors.
"""
Internationalization (i18n) module for Chakkree Tools.
Lightweight JSON-based UI translation matching IngeTrazo's native pattern.

English is the *source* language: keys passed to tr() are English strings.
Translations live in flat {english: translation} maps in chakkree_tools/i18n/<lang>.json.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

_I18N_DIR = Path(__file__).resolve().parent

LANGUAGE_NAMES: Dict[str, str] = {
    "en": "English",
    "vi": "Tiếng Việt",
    "th": "ภาษาไทย",
    "es": "Español",
}

_catalog: Dict[str, str] = {}
_lang: str = "en"
_explicitly_set: bool = False
_reverse: Optional[Dict[str, str]] = None
_reverse_of: Optional[Dict[str, str]] = None


def available_languages() -> List[str]:
    """Returns available language codes in i18n directory."""
    if not _I18N_DIR.is_dir():
        return ["en"]
    langs = sorted(p.stem for p in _I18N_DIR.glob("*.json"))
    if "en" not in langs:
        langs.insert(0, "en")
    return langs


def _detect_system_language() -> str:
    """Detects active language from IngeTrazo host, environment, or system locale."""
    # 1. Check if IngeTrazo core.i18n is available and running
    try:
        import core.i18n as ingetrazo_i18n
        host_lang = getattr(ingetrazo_i18n, "current_language", None)
        if callable(host_lang):
            hl = host_lang()
            if hl and hl in available_languages():
                return hl
    except ImportError:
        pass

    # 2. Check environment variable
    env_lang = os.environ.get("CHAKKREE_LANG") or os.environ.get("LANG", "")
    if env_lang:
        code = env_lang.split(".")[0].split("_")[0].lower()
        if code in available_languages():
            return code

    return "en"


def set_language(lang: str) -> None:
    """
    Activates language for subsequent tr() lookups.
    English loads an empty catalog (returns source string unchanged).
    """
    global _catalog, _lang, _explicitly_set, _reverse, _reverse_of
    _lang = lang or "en"
    _explicitly_set = True
    _reverse = None
    _reverse_of = None

    path = _I18N_DIR / f"{_lang}.json"
    if _lang == "en" or not path.exists():
        _catalog = {}
        return

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        _catalog = {str(k): str(v) for k, v in data.items()}
    except (OSError, ValueError):
        _catalog = {}


def get_current_language() -> str:
    """Returns currently active language code."""
    global _lang, _explicitly_set
    if not _explicitly_set:
        detected = _detect_system_language()
        if detected != _lang:
            set_language(detected)
            _explicitly_set = False  # Keep tracking dynamic changes from host
    return _lang


def source_of(text: str) -> str:
    """
    Returns English source string of a translated text.
    If text is not in catalog reverse map, returns text unchanged.
    """
    global _reverse, _reverse_of
    if _reverse_of is not _catalog:
        _reverse = {v: k for k, v in _catalog.items()}
        _reverse_of = _catalog
    return _reverse.get(text, text) if _reverse else text


def tr(text: str, /, **kwargs: Any) -> str:
    """
    Translate text into the active language; interpolate kwargs.
    If text has no translation, returns source text formatted with kwargs.
    """
    # Sync with host language if not explicitly locked by user
    if not _explicitly_set:
        get_current_language()

    out = _catalog.get(text, text)
    if kwargs:
        try:
            out = out.format(**kwargs)
        except (KeyError, IndexError, ValueError):
            try:
                out = text.format(**kwargs)
            except Exception:
                pass
    return out


# Standard gettext alias
_ = tr

__all__ = [
    "LANGUAGE_NAMES",
    "available_languages",
    "set_language",
    "get_current_language",
    "source_of",
    "tr",
    "_",
]
