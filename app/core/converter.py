"""图片转拼豆作品的主流程。"""

from __future__ import annotations

from pathlib import Path

from app.core.color_matcher import ColorMatcher
from app.core.image_processor import ResizeMode, load_and_resize
from app.core.project import BeadColor, BeadProject


class BeadConverter:
    def __init__(self, palette: list[BeadColor], palette_name: str = "") -> None:
        self.matcher = ColorMatcher(palette)
        self.palette_name = palette_name

    def convert(
        self,
        image_path: str | Path,
        width: int,
        height: int,
        mode: ResizeMode = "crop",
    ) -> BeadProject:
        image = load_and_resize(image_path, (width, height), mode)
        pixels = image.load()
        if pixels is None:
            raise RuntimeError("无法读取图片像素")

        grid = [
            [self.matcher.find_nearest(pixels[x, y]).code for x in range(width)]
            for y in range(height)
        ]
        return BeadProject(
            width=width,
            height=height,
            grid=grid,
            source_image=str(image_path),
            palette_name=self.palette_name,
        )

