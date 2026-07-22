"""将拼豆工程导出为 PNG 示意图。"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from app.core.grid_guides import coordinate_marks, is_major_grid_line
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
    coordinate_margin = max(
        24,
        len(str(max(project.width, project.height))) * 7 + 10,
    )
    grid_width = project.width * cell_size
    grid_height = project.height * cell_size
    canvas = Image.new(
        "RGB",
        (
            grid_width + coordinate_margin * 2 + 1,
            grid_height + coordinate_margin * 2 + 1,
        ),
        "white",
    )
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()

    for row_index, row in enumerate(project.grid):
        for column_index, code in enumerate(row):
            if code not in colors:
                raise ValueError(f"色板中不存在颜色编号：{code}")
            left = coordinate_margin + column_index * cell_size
            top = coordinate_margin + row_index * cell_size
            draw.ellipse(
                (
                    left,
                    top,
                    left + cell_size - 1,
                    top + cell_size - 1,
                ),
                fill=colors[code],
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

    regular_color = (150, 150, 150)
    major_color = (55, 55, 55)
    major_width = max(2, min(4, cell_size // 6))
    for line_index in range(project.width + 1):
        x = coordinate_margin + line_index * cell_size
        is_major = is_major_grid_line(line_index, project.width)
        draw.line(
            (x, coordinate_margin, x, coordinate_margin + grid_height),
            fill=major_color if is_major else regular_color,
            width=major_width if is_major else 1,
        )
    for line_index in range(project.height + 1):
        y = coordinate_margin + line_index * cell_size
        is_major = is_major_grid_line(line_index, project.height)
        draw.line(
            (coordinate_margin, y, coordinate_margin + grid_width, y),
            fill=major_color if is_major else regular_color,
            width=major_width if is_major else 1,
        )

    def draw_centered_label(center: tuple[float, float], label: str) -> None:
        text_box = draw.textbbox((0, 0), label, font=font)
        text_width = text_box[2] - text_box[0]
        text_height = text_box[3] - text_box[1]
        draw.text(
            (
                center[0] - text_width / 2,
                center[1] - text_height / 2 - text_box[1],
            ),
            label,
            fill=(35, 35, 35),
            font=font,
        )

    for coordinate in coordinate_marks(project.width):
        center_x = coordinate_margin + (coordinate - 0.5) * cell_size
        draw_centered_label((center_x, coordinate_margin / 2), str(coordinate))
        draw_centered_label(
            (center_x, coordinate_margin + grid_height + coordinate_margin / 2),
            str(coordinate),
        )
    for coordinate in coordinate_marks(project.height):
        center_y = coordinate_margin + (coordinate - 0.5) * cell_size
        draw_centered_label((coordinate_margin / 2, center_y), str(coordinate))
        draw_centered_label(
            (coordinate_margin + grid_width + coordinate_margin / 2, center_y),
            str(coordinate),
        )

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(destination, format="PNG")
    return destination

