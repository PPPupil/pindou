"""图片转拼豆作品的主流程。"""

from __future__ import annotations

from pathlib import Path

from app.core.color_matcher import ColorMatcher
from app.core.color_simplifier import (
    merge_small_regions,
    merge_similar_neighbors,
    quantize_image,
    remove_rare_color_outliers,
    resolve_output_color_limit,
)
from app.core.image_processor import ImageStyle, ResizeMode, load_and_resize, resolve_image_style
from app.core.project import BeadColor, BeadProject
from app.core.palette_tiers import colors_for_palette_level, resolve_palette_level


class BeadConverter:
    def __init__(self, palette: list[BeadColor], palette_name: str = "") -> None:
        self.palette = tuple(palette)
        self.palette_name = palette_name

    def convert(
        self,
        image_path: str | Path,
        width: int,
        height: int,
        mode: ResizeMode = "crop",
        palette_level: int = 221,
        image_style: ImageStyle = "auto",
        color_limit: int = 0,
        outlier_max_count: int = 1,
    ) -> BeadProject:
        resolved_style = resolve_image_style(image_path, image_style)
        resolved_level = resolve_palette_level(palette_level, width, height)
        selected_palette = colors_for_palette_level(self.palette, resolved_level)
        matcher = ColorMatcher(selected_palette)
        resolved_color_limit = resolve_output_color_limit(
            color_limit,
            width,
            height,
            resolved_style,
            len(matcher.palette),
        )
        image = load_and_resize(
            image_path,
            (width, height),
            mode,
            image_style=resolved_style,
            color_limit=resolved_color_limit,
        )
        image = quantize_image(image, resolved_color_limit)
        pixels = image.load()
        if pixels is None:
            raise RuntimeError("无法读取图片像素")

        grid = [
            [matcher.find_nearest(pixels[x, y]).code for x in range(width)]
            for y in range(height)
        ]
        if resolved_style == "cartoon":
            grid = merge_similar_neighbors(grid, matcher.palette, passes=2)
            grid = merge_small_regions(
                grid,
                matcher.palette,
                max_region_size=3,
                distance_threshold=28,
                passes=2,
            )
        else:
            grid = merge_similar_neighbors(grid, matcher.palette, passes=1)
            grid = merge_small_regions(
                grid,
                matcher.palette,
                max_region_size=1,
                distance_threshold=18,
                passes=1,
            )
        grid, outliers_removed = remove_rare_color_outliers(
            grid,
            matcher.palette,
            max_global_count=outlier_max_count,
        )
        return BeadProject(
            width=width,
            height=height,
            grid=grid,
            source_image=str(image_path),
            palette_name=self.palette_name,
            palette_level=resolved_level,
            image_style=resolved_style,
            color_limit=resolved_color_limit,
            outliers_removed=outliers_removed,
        )
