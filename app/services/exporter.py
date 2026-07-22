"""将拼豆工程导出为 PNG 示意图。"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

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
    font = ImageFont.load_default()

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
            if cell_size >= 16:
                brightness = (
                    0.299 * colors[code][0]
                    + 0.587 * colors[code][1]
                    + 0.114 * colors[code][2]
                )
                text_box = draw.textbbox((0, 0), code, font=font)
                text_width = text_box[2] - text_box[0]
                text_height = text_box[3] - text_box[1]
                draw.text(
                    (
                        left + (cell_size - text_width) / 2,
                        top + (cell_size - text_height) / 2 - text_box[1],
                    ),
                    code,
                    fill="black" if brightness > 150 else "white",
                    font=font,
                )

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(destination, format="PNG")
    return destination

