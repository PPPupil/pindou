"""加载 JSON 格式的拼豆色板。"""

from __future__ import annotations

import colorsys
import json
from dataclasses import dataclass
from pathlib import Path

from app.core.project import BeadColor


def approximate_chinese_color_name(
    rgb: tuple[int, int, int],
    transparent: bool = False,
) -> str:
    """根据 RGB 生成描述性中文色名，不代表品牌官方命名。"""
    if transparent:
        return "透明色"

    red, green, blue = (channel / 255 for channel in rgb)
    hue, saturation, value = colorsys.rgb_to_hsv(red, green, blue)
    hue_degrees = hue * 360

    if saturation < 0.1:
        if value >= 0.92:
            return "白色"
        if value >= 0.72:
            return "浅灰色"
        if value >= 0.45:
            return "灰色"
        if value >= 0.2:
            return "深灰色"
        return "黑色"

    if 15 <= hue_degrees < 45 and value < 0.65:
        base_name = "棕色"
    elif hue_degrees < 15 or hue_degrees >= 345:
        base_name = "红色"
    elif hue_degrees < 40:
        base_name = "橙色"
    elif hue_degrees < 68:
        base_name = "黄色"
    elif hue_degrees < 88:
        base_name = "黄绿色"
    elif hue_degrees < 155:
        base_name = "绿色"
    elif hue_degrees < 190:
        base_name = "青色"
    elif hue_degrees < 220:
        base_name = "天蓝色"
    elif hue_degrees < 255:
        base_name = "蓝色"
    elif hue_degrees < 290:
        base_name = "紫色"
    elif hue_degrees < 335:
        base_name = "粉色"
    else:
        base_name = "玫红色"

    if value <= 0.48:
        return f"深{base_name}"
    if value >= 0.88 and saturation <= 0.65:
        return f"浅{base_name}"
    if saturation <= 0.28:
        return f"灰{base_name}"
    return base_name


@dataclass(frozen=True, slots=True)
class Palette:
    brand: str
    bead_size_mm: float
    colors: list[BeadColor]
    palette_id: str = ""
    version: str = ""
    color_space: str = "sRGB"
    source: str = ""
    accuracy: str = ""
    notes: tuple[str, ...] = ()


def load_palette(path: str | Path) -> Palette:
    with Path(path).open("r", encoding="utf-8") as file:
        data = json.load(file)

    metadata = data.get("palette", {})
    colors = []
    for item in data["colors"]:
        rgb = tuple(item["rgb"])
        transparent = bool(item.get("transparent", False))
        colors.append(
            BeadColor(
                code=item["code"],
                name=item.get("name")
                or approximate_chinese_color_name(rgb, transparent),
                rgb=rgb,
                hex_value=item.get("hex", ""),
                source_row=item.get("sourceRow"),
                source_column=item.get("sourceColumn"),
                transparent=transparent,
                note=item.get("note", ""),
            )
        )
    if not colors:
        raise ValueError("色板至少需要一种颜色")
    declared_count = metadata.get("colorCount")
    if declared_count is not None and int(declared_count) != len(colors):
        raise ValueError(
            f"色板声明包含 {declared_count} 色，但实际读取到 {len(colors)} 色"
        )
    codes = [color.code for color in colors]
    if len(set(codes)) != len(codes):
        raise ValueError("色板中存在重复色号")
    return Palette(
        brand=data.get("brand", metadata.get("displayName", "未命名色板")),
        bead_size_mm=float(data.get("bead_size_mm", metadata.get("beadSizeMm", 5))),
        colors=colors,
        palette_id=metadata.get("id", ""),
        version=metadata.get("version", ""),
        color_space=metadata.get("colorSpace", "sRGB"),
        source=metadata.get("source", ""),
        accuracy=metadata.get("accuracy", ""),
        notes=tuple(metadata.get("notes", ())),
    )

