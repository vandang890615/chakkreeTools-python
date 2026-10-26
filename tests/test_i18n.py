"""
Unit tests for Chakkree Tools Internationalization (i18n) System.
Tests catalog loading, fallback behaviour, formatting interpolation,
reverse source lookup, and UI dialog integration across English, Vietnamese, Thai, and Spanish.
"""

import json
import os
from pathlib import Path
import pytest

from chakkree_tools.i18n import (
    LANGUAGE_NAMES,
    available_languages,
    get_current_language,
    set_language,
    source_of,
    tr,
)


@pytest.fixture(autouse=True)
def reset_to_english():
    """Ensure each test starts and ends with English default language."""
    set_language("en")
    yield
    set_language("en")


def test_i18n_available_languages():
    langs = available_languages()
    assert "en" in langs
    assert "vi" in langs
    assert "th" in langs
    assert "es" in langs

    assert LANGUAGE_NAMES["en"] == "English"
    assert LANGUAGE_NAMES["vi"] == "Tiếng Việt"
    assert LANGUAGE_NAMES["th"] == "ภาษาไทย"
    assert LANGUAGE_NAMES["es"] == "Español"


def test_i18n_default_english_fallback():
    set_language("en")
    assert get_current_language() == "en"

    # Exact string matching
    assert tr("Footing Parameters") == "Footing Parameters"
    assert tr("Create Pile Cap (1-9 Piles)...") == "Create Pile Cap (1-9 Piles)..."
    assert tr("Beam Parameters") == "Beam Parameters"
    assert tr("Column Parameters") == "Column Parameters"

    # Kwargs interpolation
    assert tr("Invalid input: {exc}", exc="TestError") == "Invalid input: TestError"
    assert tr("Exported .debim to {name}", name="house.debim") == "Exported .debim to house.debim"

    # Unknown key returns key unchanged
    assert tr("Nonexistent Key Here 12345") == "Nonexistent Key Here 12345"


def test_i18n_vietnamese_catalog():
    set_language("vi")
    assert get_current_language() == "vi"

    # Dialog & structural terms in Vietnamese
    assert tr("Footing Parameters") == "Thông số đài móng"
    assert tr("Create Pile Cap (1-9 Piles)...") == "Tạo đài móng cọc (1-9 cọc)..."
    assert tr("Beam Parameters") == "Thông số dầm"
    assert tr("Column Parameters") == "Thông số cột"
    assert tr("Slab Parameters") == "Thông số ô sàn"
    assert tr("Rebar Tools") == "Công cụ cốt thép"
    assert tr("QTO Take-off") == "Dự toán QTO"
    assert tr("Export Model to .debim...") == "Xuất khẩu mô hình sang .debim..."
    assert tr("Rebar Color Configuration") == "Cấu hình màu sắc cốt thép theo đường kính"
    assert tr("Precast Plank Slab (PS)") == "Sàn panel lắp ghép (PS)"
    assert tr("Cast-in-place RC Slab (RC)") == "Sàn toàn khối đổ tại chỗ (RC)"

    # Format parameter interpolation in Vietnamese
    assert tr("Total Elements: {count}", count=12) == "Tổng số cấu kiện: 12"
    assert tr("Exported .debim to {name}", name="model.debim") == "Đã xuất file .debim sang model.debim"


def test_i18n_thai_catalog():
    set_language("th")
    assert get_current_language() == "th"

    assert tr("Rebar Tools") == "เครื่องมือเหล็กเสริม"
    assert tr("Create Pile Cap (1-9 Piles)...") == "สร้างฐานรากเสาเข็ม (1-9 ต้น)..."
    assert tr("Footing Parameters") == "พารามิเตอร์ฐานราก"
    assert tr("QTO Take-off") == "ถอดปริมาณ QTO"


def test_i18n_spanish_catalog():
    set_language("es")
    assert get_current_language() == "es"

    assert tr("Rebar Tools") == "Herramientas de armadura"
    assert tr("Create Pile Cap (1-9 Piles)...") == "Crear zapata con pilotes (1-9 pilotes)..."
    assert tr("About") == "Acerca de"


def test_i18n_source_of_reverse_lookup():
    set_language("vi")

    # Reverse translated string to English source
    assert source_of("Thông số đài móng") == "Footing Parameters"
    assert source_of("Tạo đài móng cọc (1-9 cọc)...") == "Create Pile Cap (1-9 Piles)..."
    assert source_of("Công cụ cốt thép") == "Rebar Tools"

    # Untranslated or unknown text returns identical
    assert source_of("Unknown String") == "Unknown String"


def test_i18n_json_catalogs_valid_format():
    i18n_dir = Path(__file__).resolve().parent.parent / "chakkree_tools" / "i18n"
    assert i18n_dir.is_dir()

    for p in i18n_dir.glob("*.json"):
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert isinstance(data, dict), f"{p.name} must be a JSON dictionary"
            for k, v in data.items():
                assert isinstance(k, str) and len(k) > 0, f"Empty key in {p.name}"
                assert isinstance(v, str), f"Value for '{k}' in {p.name} must be a string"


def test_i18n_dialogs_rendering_vietnamese():
    try:
        from PySide6.QtWidgets import QApplication
        from chakkree_tools.ingetrazo_plugin.ui.footing_dialog import FootingDialog
        from chakkree_tools.ingetrazo_plugin.ui.column_dialog import ColumnDialog
        from chakkree_tools.ingetrazo_plugin.ui.beam_dialog import BeamDialog
        from chakkree_tools.ingetrazo_plugin.ui.slab_dialog import SlabDialog
    except ImportError:
        pytest.skip("PySide6 not installed")

    app = QApplication.instance()
    if app is None:
        app = QApplication([])

    set_language("vi")

    f_dlg = FootingDialog()
    assert f_dlg.windowTitle() == "Móng tham số / Đài cọc"
    assert "Kích thước móng:" in f_dlg.calc_info_label.text()
    assert "Bê tông:" in f_dlg.calc_info_label.text()

    c_dlg = ColumnDialog()
    assert c_dlg.windowTitle() == "Cột bê tông cốt thép tham số"
    assert "Tiết diện:" in c_dlg.calc_info_label.text()
    assert "Bê tông:" in c_dlg.calc_info_label.text()

    b_dlg = BeamDialog()
    assert b_dlg.windowTitle() == "Dầm bê tông cốt thép tham số"
    assert "Nhịp:" in b_dlg.calc_info_label.text()

    s_dlg = SlabDialog()
    assert s_dlg.windowTitle() == "Sàn bê tông cốt thép / Sàn panel tham số"
    assert "Diện tích:" in s_dlg.calc_info_label.text()
