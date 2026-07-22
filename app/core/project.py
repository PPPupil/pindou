"""拼豆色与作品的数据模型。"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class BeadColor:
    code: str
    name: str
    rgb: tuple[int, int, int]

    def __post_init__(self) -> None:
        if len(self.rgb) != 3 or any(not 0 <= channel <= 255 for channel in self.rgb):
            raise ValueError("RGB 通道必须是 0 到 255 之间的三个整数")


@dataclass(slots=True)
class BeadProject:
    width: int
    height: int
    grid: list[list[str]] = field(default_factory=list)
    source_image: str | None = None
    palette_name: str = ""

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("作品宽高必须大于零")
        if self.grid:
            if len(self.grid) != self.height or any(len(row) != self.width for row in self.grid):
                raise ValueError("网格尺寸与作品宽高不一致")

    @property
    def total_beads(self) -> int:
        return self.width * self.height

    def color_counts(self) -> Counter[str]:
        return Counter(code for row in self.grid for code in row)

