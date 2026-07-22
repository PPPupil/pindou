from pathlib import Path

from app.core.color_matcher import ColorMatcher
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

    matcher = ColorMatcher(palette.colors)
    assert matcher.find_nearest((255, 255, 255)).code == "H2"
