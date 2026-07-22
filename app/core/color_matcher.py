"""将图像像素匹配到拼豆色板。"""

from __future__ import annotations

from collections.abc import Iterable

from app.core.project import BeadColor


class ColorMatcher:
    """第一版使用 RGB 平方距离；后续可替换为 Lab/CIEDE2000。"""

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

    def find_nearest(self, rgb: tuple[int, int, int]) -> BeadColor:
        return min(self.palette, key=lambda color: self._distance_squared(rgb, color.rgb))

    @staticmethod
    def _distance_squared(left: tuple[int, int, int], right: tuple[int, int, int]) -> int:
        return sum((a - b) ** 2 for a, b in zip(left, right, strict=True))

