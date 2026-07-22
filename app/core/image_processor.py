"""读取、处理透明度并把图片缩放到目标豆数。"""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Literal

from PIL import Image, ImageChops, ImageOps, ImageStat

ResizeMode = Literal["crop", "contain", "stretch"]
ImageStyle = Literal["auto", "cartoon", "photo"]


def _composite_rgb(source: Image.Image, background: tuple[int, int, int]) -> Image.Image:
    rgba = source.convert("RGBA")
    base = Image.new("RGBA", rgba.size, (*background, 255))
    base.alpha_composite(rgba)
    return base.convert("RGB")


def detect_image_style(image_path: str | Path) -> Literal["cartoon", "photo"]:
    """根据压缩到少量颜色后的误差，粗略判断图片是否是平涂插画。"""
    with Image.open(image_path) as source:
        sample = _composite_rgb(source, (255, 255, 255))
        sample.thumbnail((128, 128), Image.Resampling.BOX)
        reduced = sample.quantize(
            colors=16,
            method=Image.Quantize.MEDIANCUT,
            dither=Image.Dither.NONE,
        ).convert("RGB")
        difference = ImageChops.difference(sample, reduced)
        mean_error = sum(ImageStat.Stat(difference).mean) / 3
        # 小尺寸网络图片往往带有轻微 JPEG 噪声，适当放宽平涂图判断。
        threshold = 18.0 if min(source.size) <= 256 else 13.0
        return "cartoon" if mean_error <= threshold else "photo"


def resolve_image_style(
    image_path: str | Path,
    requested_style: ImageStyle,
) -> Literal["cartoon", "photo"]:
    if requested_style == "auto":
        return detect_image_style(image_path)
    if requested_style not in ("cartoon", "photo"):
        raise ValueError(f"不支持的图像类型：{requested_style}")
    return requested_style


def _resize_for_mode(
    image: Image.Image,
    size: tuple[int, int],
    mode: ResizeMode,
    method: Image.Resampling,
    background: tuple[int, int, int],
) -> Image.Image:
    if mode == "crop":
        return ImageOps.fit(image, size, method=method)
    if mode == "contain":
        return ImageOps.pad(image, size, method=method, color=background)
    if mode == "stretch":
        return image.resize(size, method)
    raise ValueError(f"不支持的缩放模式：{mode}")


def _relative_luminance(rgb: tuple[int, int, int]) -> float:
    return 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]


def _cartoon_dominant_resize(
    image: Image.Image,
    size: tuple[int, int],
    mode: ResizeMode,
    background: tuple[int, int, int],
    color_limit: int,
) -> Image.Image:
    """按每颗豆覆盖区域的主色采样，并优先保留真正的深色轮廓。"""
    width, height = size
    sample_factor = 4
    sample_size = (width * sample_factor, height * sample_factor)

    # 最近邻只搬运原图颜色，不制造 BOX/LANCZOS 的灰色过渡带。
    sampled = _resize_for_mode(
        image,
        sample_size,
        mode,
        Image.Resampling.NEAREST,
        background,
    )
    simplified = sampled.quantize(
        colors=max(2, min(color_limit, 256)),
        method=Image.Quantize.MEDIANCUT,
        dither=Image.Dither.NONE,
    ).convert("RGB")

    sampled_pixels = sampled.load()
    simplified_pixels = simplified.load()
    if sampled_pixels is None or simplified_pixels is None:
        raise RuntimeError("无法读取卡通图片像素")

    result = Image.new("RGB", size, background)
    result_pixels = result.load()
    if result_pixels is None:
        raise RuntimeError("无法创建卡通采样结果")

    # 16 个采样点中至少 4 个是实质深色才视为轮廓，既保线又避免向背景膨胀。
    outline_sample_threshold = 4
    for target_y in range(height):
        start_y = target_y * sample_factor
        for target_x in range(width):
            start_x = target_x * sample_factor
            dark_sample_count = 0
            dominant_colors: Counter[tuple[int, int, int]] = Counter()
            for offset_y in range(sample_factor):
                for offset_x in range(sample_factor):
                    sample_x = start_x + offset_x
                    sample_y = start_y + offset_y
                    original = sampled_pixels[sample_x, sample_y]
                    if _relative_luminance(original) <= 78:
                        dark_sample_count += 1
                    dominant_colors[simplified_pixels[sample_x, sample_y]] += 1

            if dark_sample_count >= outline_sample_threshold:
                # 后续会把纯黑匹配到当前色卡中最黑的实体豆，避免落到 B23 等近黑色。
                result_pixels[target_x, target_y] = (0, 0, 0)
            else:
                # 灰边/浅色抗锯齿通常只占少数，直接归入覆盖面积最大的背景主色。
                result_pixels[target_x, target_y] = dominant_colors.most_common(1)[0][0]

    return result


def load_and_resize(
    image_path: str | Path,
    size: tuple[int, int],
    mode: ResizeMode = "crop",
    background: tuple[int, int, int] = (255, 255, 255),
    image_style: Literal["cartoon", "photo"] = "photo",
    color_limit: int = 24,
) -> Image.Image:
    """返回大小等于目标豆数的 RGB 图片，每个像素对应一颗豆。"""
    width, height = size
    if width <= 0 or height <= 0:
        raise ValueError("目标尺寸必须大于零")
    if image_style not in ("cartoon", "photo"):
        raise ValueError(f"不支持的图像类型：{image_style}")
    if color_limit < 2:
        raise ValueError("颜色上限必须至少为 2")

    with Image.open(image_path) as source:
        rgb_image = _composite_rgb(source, background)
        if image_style == "cartoon":
            result = _cartoon_dominant_resize(
                rgb_image,
                size,
                mode,
                background,
                color_limit,
            )
        else:
            result = _resize_for_mode(
                rgb_image,
                size,
                mode,
                Image.Resampling.LANCZOS,
                background,
            )

    return result
