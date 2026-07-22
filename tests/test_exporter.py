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
        assert image.size == (21, 11)

