from PIL import Image

from app.core.project import BeadColor, BeadProject
from app.services.exporter import export_png


def test_exporter_creates_png(tmp_path) -> None:
    project = BeadProject(width=2, height=1, grid=[["R", "W"]])
    palette = [
        BeadColor("R", "红", (255, 0, 0)),
        BeadColor("W", "白", (255, 255, 255)),
    ]
    destination = tmp_path / "pattern.png"

    export_png(project, palette, destination, cell_size=10)

    assert destination.exists()
    with Image.open(destination) as image:
        assert image.size == (69, 59)
        margin = 24
        assert image.getpixel((margin + 5, margin + 5)) == (255, 0, 0)
        first_cell_pixels = {
            image.getpixel((margin + x, margin + y))
            for x in range(2, 9)
            for y in range(2, 9)
        }
        assert (255, 255, 255) in first_cell_pixels


def test_exporter_draws_five_cell_guides_and_four_side_coordinates(tmp_path) -> None:
    project = BeadProject(
        width=6,
        height=6,
        grid=[["W"] * 6 for _ in range(6)],
    )
    palette = [BeadColor("W", "白", (255, 255, 255))]
    destination = tmp_path / "guided-pattern.png"

    export_png(project, palette, destination, cell_size=10)

    with Image.open(destination) as image:
        margin = 24
        regular_line = image.getpixel((margin + 4 * 10, margin + 2))
        major_line = image.getpixel((margin + 5 * 10, margin + 2))
        assert major_line == (55, 55, 55)
        assert regular_line == (150, 150, 150)

        top_margin = image.crop((0, 0, image.width, margin))
        bottom_margin = image.crop((0, margin + 60, image.width, image.height))
        left_margin = image.crop((0, 0, margin, image.height))
        right_margin = image.crop((margin + 60, 0, image.width, image.height))
        assert top_margin.convert("L").getextrema()[0] < 100
        assert bottom_margin.convert("L").getextrema()[0] < 100
        assert left_margin.convert("L").getextrema()[0] < 100
        assert right_margin.convert("L").getextrema()[0] < 100
