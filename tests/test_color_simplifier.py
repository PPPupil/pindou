from PIL import Image

from app.core.color_simplifier import (
    automatic_output_color_limit,
    merge_similar_neighbors,
    merge_small_regions,
    quantize_image,
    remove_rare_color_outliers,
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


def test_rare_similar_outlier_is_removed_but_dark_detail_is_preserved() -> None:
    palette = [
        BeadColor("BASE", "白色", (238, 236, 232)),
        BeadColor("ODD", "近似白色", (226, 225, 222)),
        BeadColor("EYE", "黑色", (35, 35, 34)),
    ]
    grid = [
        ["BASE", "BASE", "BASE", "BASE", "BASE"],
        ["BASE", "ODD", "BASE", "EYE", "BASE"],
        ["BASE", "BASE", "BASE", "BASE", "BASE"],
    ]

    cleaned, removed_count = remove_rare_color_outliers(grid, palette)

    assert cleaned[1][1] == "BASE"
    assert cleaned[1][3] == "EYE"
    assert removed_count == 1


def test_rare_outlier_cleanup_can_be_disabled() -> None:
    palette = [
        BeadColor("A", "灰色", (120, 120, 120)),
        BeadColor("B", "近似灰色", (125, 125, 125)),
    ]
    grid = [["A", "A", "A"], ["A", "B", "A"]]

    cleaned, removed_count = remove_rare_color_outliers(
        grid,
        palette,
        max_global_count=0,
    )

    assert cleaned == grid
    assert removed_count == 0


def test_real_e11_and_e17_singletons_merge_into_neighboring_e8() -> None:
    palette = [
        BeadColor("E8", "白色", (239, 219, 232)),
        BeadColor("E11", "白色", (241, 219, 217)),
        BeadColor("E17", "白色", (242, 225, 231)),
    ]
    grid = [
        ["E8", "E8", "E8", "E8"],
        ["E8", "E11", "E8", "E8"],
        ["E8", "E8", "E17", "E8"],
        ["E8", "E8", "E8", "E8"],
    ]

    cleaned, removed_count = remove_rare_color_outliers(grid, palette)

    assert all(code == "E8" for row in cleaned for code in row)
    assert removed_count == 2
