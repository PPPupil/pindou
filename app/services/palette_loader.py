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


def load_palette(path: str | Path) -> Palette:
    with Path(path).open("r", encoding="utf-8") as file:
        data = json.load(file)

    colors = [
        BeadColor(
            code=item["code"],
            name=item["name"],
            rgb=tuple(item["rgb"]),
        )
        for item in data["colors"]
    ]
    if not colors:
        raise ValueError("色板至少需要一种颜色")
    return Palette(
        brand=data["brand"],
        bead_size_mm=float(data["bead_size_mm"]),
        colors=colors,
    )

