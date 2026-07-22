"""将拼豆工程导出为 PNG 示意图。"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from app.core.project import BeadColor, BeadProject


def export_png(
    project: BeadProject,
    palette: list[BeadColor],
    output_path: str | Path,
    cell_size: int = 20,
) -> Path:
    if not project.grid:
        raise ValueError("不能导出空作品")
    if cell_size < 2:
        raise ValueError("单元格尺寸至少为 2 像素")

    colors = {color.code: color.rgb for color in palette}
    canvas = Image.new(
        "RGB",
        (project.width * cell_size + 1, project.height * cell_size + 1),
        "white",
    )
    draw = ImageDraw.Draw(canvas)

    for row_index, row in enumerate(project.grid):
        for column_index, code in enumerate(row):
            if code not in colors:
                raise ValueError(f"色板中不存在颜色编号：{code}")
            left = column_index * cell_size
            top = row_index * cell_size
            draw.rectangle(
                (left, top, left + cell_size, top + cell_size),
                fill=colors[code],
                outline=(120, 120, 120),
            )

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(destination, format="PNG")
    return destination

