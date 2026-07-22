from pathlib import Path

from app.core.color_matcher import ColorMatcher
from app.core.project import color_code_sort_key
from app.services.palette_loader import load_palette


def test_marketplace_palette_loads_all_221_colors() -> None:
    palette_path = Path(__file__).resolve().parents[1] / "mard_221_approx_from_chart.json"

    palette = load_palette(palette_path)

    assert len(palette.colors) == 221
    assert len({color.code for color in palette.colors}) == 221
    assert palette.accuracy == "approximate"
    assert palette.color_space == "sRGB"

    transparent = [color for color in palette.colors if color.transparent]
    assert len(transparent) == 1
    assert transparent[0].code == "H1"
    assert transparent[0].source_row == 2
    assert transparent[0].source_column == 1
    assert transparent[0].name == "透明色"
    assert all(color.name != color.code for color in palette.colors)

    matcher = ColorMatcher(palette.colors)
    assert matcher.find_nearest((255, 255, 255)).code == "H2"


def test_color_codes_use_natural_letter_and_number_order() -> None:
    codes = ["B1", "A10", "A2", "A1", "C3"]

    assert sorted(codes, key=color_code_sort_key) == ["A1", "A2", "A10", "B1", "C3"]
