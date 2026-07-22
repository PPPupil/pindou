"""可选的 Floyd–Steinberg 误差扩散算法。"""

from __future__ import annotations

import numpy as np
from PIL import Image

from app.core.color_matcher import ColorMatcher


def floyd_steinberg(image: Image.Image, matcher: ColorMatcher) -> Image.Image:
    """将误差扩散后的图片量化到 matcher 的色板。"""
    pixels = np.asarray(image.convert("RGB"), dtype=np.float32).copy()
    height, width, _ = pixels.shape

    for y in range(height):
        for x in range(width):
            old = pixels[y, x]
            old_rgb = tuple(int(value) for value in np.clip(old, 0, 255))
            new = np.asarray(matcher.find_nearest(old_rgb).rgb, dtype=np.float32)
            pixels[y, x] = new
            error = old - new

            if x + 1 < width:
                pixels[y, x + 1] += error * 7 / 16
            if y + 1 < height:
                if x > 0:
                    pixels[y + 1, x - 1] += error * 3 / 16
                pixels[y + 1, x] += error * 5 / 16
                if x + 1 < width:
                    pixels[y + 1, x + 1] += error * 1 / 16

    return Image.fromarray(np.clip(pixels, 0, 255).astype(np.uint8), mode="RGB")

