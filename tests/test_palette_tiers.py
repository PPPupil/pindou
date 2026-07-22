from pathlib import Path

from app.core.palette_tiers import (
    PALETTE_LEVELS,
    TIER_CODES,
    automatic_palette_level,
    colors_for_palette_level,
)
from app.services.palette_loader import load_palette


def test_automatic_palette_levels_use_30_50_100_boundaries() -> None:
    assert automatic_palette_level(29, 200) == 24
    assert automatic_palette_level(30, 200) == 48
    assert automatic_palette_level(49, 200) == 48
    assert automatic_palette_level(50, 200) == 96
    assert automatic_palette_level(99, 200) == 96
    assert automatic_palette_level(100, 200) == 221


def test_mard_tiers_have_exact_nested_counts() -> None:
    assert PALETTE_LEVELS == (24, 48, 72, 96, 120, 221)
    previous_codes: set[str] = set()
    for level in (24, 48, 72, 96, 120):
        codes = TIER_CODES[level]
        assert len(codes) == level
        assert previous_codes <= set(codes)
        previous_codes = set(codes)
    assert [code for code in TIER_CODES[72] if code == "D19"] == ["D19", "D19"]


def test_every_tier_code_exists_in_221_color_file() -> None:
    palette_path = Path(__file__).resolve().parents[1] / "mard_221_approx_from_chart.json"
    palette = load_palette(palette_path)

    for level in (24, 48, 72, 96, 120):
        selected = colors_for_palette_level(palette.colors, level)
        assert len(selected) == len(set(TIER_CODES[level]))
