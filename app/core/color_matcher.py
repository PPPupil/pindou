"""将图像像素匹配到拼豆色板。"""

from __future__ import annotations

from collections.abc import Iterable

from app.core.color_space import lab_distance_squared, rgb_to_lab
from app.core.project import BeadColor


class ColorMatcher:
    """使用 CIE Lab 距离把图像颜色匹配到最接近的实体拼豆色。"""

    def __init__(
        self,
        palette: Iterable[BeadColor],
        include_transparent: bool = False,
    ) -> None:
        self.palette = tuple(
            color for color in palette if include_transparent or not color.transparent
        )
        if not self.palette:
            raise ValueError("色板中没有可用于自动匹配的不透明颜色")
        self._palette_lab = tuple(
            (color, rgb_to_lab(color.rgb)) for color in self.palette
        )

    def find_nearest(self, rgb: tuple[int, int, int]) -> BeadColor:
        target_lab = rgb_to_lab(rgb)
        return min(
            self._palette_lab,
            key=lambda item: lab_distance_squared(target_lab, item[1]),
        )[0]

