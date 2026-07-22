"""将图像像素匹配到拼豆色板。"""

from __future__ import annotations

from collections.abc import Iterable

from app.core.project import BeadColor


class ColorMatcher:
    """第一版使用 RGB 平方距离；后续可替换为 Lab/CIEDE2000。"""

    def __init__(self, palette: Iterable[BeadColor]) -> None:
        self.palette = tuple(palette)
        if not self.palette:
            raise ValueError("色板不能为空")

    def find_nearest(self, rgb: tuple[int, int, int]) -> BeadColor:
        return min(self.palette, key=lambda color: self._distance_squared(rgb, color.rgb))

    @staticmethod
    def _distance_squared(left: tuple[int, int, int], right: tuple[int, int, int]) -> int:
        return sum((a - b) ** 2 for a, b in zip(left, right, strict=True))

