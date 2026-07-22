from PIL import Image

from app.core.color_simplifier import (
    automatic_output_color_limit,
    merge_similar_neighbors,
    merge_small_regions,
    quantize_image,
    resolve_output_color_limit,
)
from app.core.project import BeadColor


def test_small_image_uses_limited_number_of_colors() -> None:
    values = [round(index * 255 / 19) for index in range(20)]
    image = Image.new("RGB", (20, 1))
    image.putdata([(value, value, value) for value in values])
    simplified = quantize_image(image, 8)

    assert len(simplified.getcolors(maxcolors=256)) <= 8


def test_similar_isolated_color_merges_but_distinct_color_remains() -> None:
    palette = [
        BeadColor("A1", "灰色", (100, 100, 100)),
        BeadColor("A2", "浅灰色", (115, 115, 115)),
        BeadColor("A3", "白色", (240, 240, 240)),
    ]
    similar_grid = [
        ["A1", "A1", "A1"],
        ["A1", "A2", "A1"],
        ["A1", "A1", "A1"],
    ]
    distinct_grid = [
        ["A1", "A1", "A1"],
        ["A1", "A3", "A1"],
        ["A1", "A1", "A1"],
    ]

    assert merge_similar_neighbors(similar_grid, palette)[1][1] == "A1"
    assert merge_similar_neighbors(distinct_grid, palette)[1][1] == "A3"


def test_cartoon_color_limit_is_separate_from_available_palette() -> None:
    assert automatic_output_color_limit(24, 40, "cartoon") == 12
    assert automatic_output_color_limit(40, 40, "cartoon") == 16
    assert automatic_output_color_limit(60, 80, "cartoon") == 24
    assert automatic_output_color_limit(120, 100, "cartoon") == 32
    assert resolve_output_color_limit(48, 20, 20, "cartoon", 24) == 24


def test_small_similar_region_merges_without_erasing_dark_outline() -> None:
    palette = [
        BeadColor("SKIN", "肤色", (240, 195, 165)),
        BeadColor("NOISE", "相近肤色", (226, 184, 158)),
        BeadColor("LINE", "轮廓", (55, 38, 37)),
    ]
    grid = [
        ["SKIN", "SKIN", "SKIN", "SKIN", "SKIN"],
        ["SKIN", "NOISE", "NOISE", "SKIN", "SKIN"],
        ["SKIN", "SKIN", "SKIN", "LINE", "SKIN"],
        ["SKIN", "SKIN", "SKIN", "SKIN", "SKIN"],
    ]

    merged = merge_small_regions(grid, palette)

    assert merged[1][1:3] == ["SKIN", "SKIN"]
    assert merged[2][3] == "LINE"
