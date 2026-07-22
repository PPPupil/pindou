"""读取、处理透明度并把图片缩放到目标豆数。"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from PIL import Image, ImageOps

ResizeMode = Literal["crop", "contain", "stretch"]


def load_and_resize(
    image_path: str | Path,
    size: tuple[int, int],
    mode: ResizeMode = "crop",
    background: tuple[int, int, int] = (255, 255, 255),
) -> Image.Image:
    """返回大小等于目标豆数的 RGB 图片，每个像素对应一颗豆。"""
    width, height = size
    if width <= 0 or height <= 0:
        raise ValueError("目标尺寸必须大于零")

    with Image.open(image_path) as source:
        rgba = source.convert("RGBA")
        base = Image.new("RGBA", rgba.size, (*background, 255))
        base.alpha_composite(rgba)
        rgb_image = base.convert("RGB")

        if mode == "crop":
            result = ImageOps.fit(rgb_image, size, method=Image.Resampling.LANCZOS)
        elif mode == "contain":
            result = ImageOps.pad(
                rgb_image,
                size,
                method=Image.Resampling.LANCZOS,
                color=background,
            )
        elif mode == "stretch":
            result = rgb_image.resize(size, Image.Resampling.LANCZOS)
        else:
            raise ValueError(f"不支持的缩放模式：{mode}")

    return result

