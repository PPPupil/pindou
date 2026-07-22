"""颜色空间转换工具。"""

from __future__ import annotations

from math import pow


LabColor = tuple[float, float, float]


def rgb_to_lab(rgb: tuple[int, int, int]) -> LabColor:
    """把 sRGB 转为 CIE Lab（D65），用于更接近人眼感知的颜色比较。"""
    linear = []
    for channel in rgb:
        value = channel / 255.0
        linear.append(
            value / 12.92
            if value <= 0.04045
            else pow((value + 0.055) / 1.055, 2.4)
        )

    red, green, blue = linear
    x = (red * 0.4124564 + green * 0.3575761 + blue * 0.1804375) / 0.95047
    y = red * 0.2126729 + green * 0.7151522 + blue * 0.0721750
    z = (red * 0.0193339 + green * 0.1191920 + blue * 0.9503041) / 1.08883

    def pivot(value: float) -> float:
        return pow(value, 1 / 3) if value > 0.008856 else 7.787 * value + 16 / 116

    fx, fy, fz = pivot(x), pivot(y), pivot(z)
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)


def lab_distance_squared(left: LabColor, right: LabColor) -> float:
    """返回 Lab 欧氏距离的平方，省去最近色搜索时不必要的开方。"""
    return sum((a - b) ** 2 for a, b in zip(left, right, strict=True))
