"""加载 JSON 格式的拼豆色板。"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from app.core.project import BeadColor


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
    colors = [
        BeadColor(
            code=item["code"],
            name=item.get("name", item["code"]),
            rgb=tuple(item["rgb"]),
            hex_value=item.get("hex", ""),
            source_row=item.get("sourceRow"),
            source_column=item.get("sourceColumn"),
            transparent=bool(item.get("transparent", False)),
            note=item.get("note", ""),
        )
        for item in data["colors"]
    ]
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

