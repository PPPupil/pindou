from PIL import Image

from app.core.converter import BeadConverter
from app.core.project import BeadColor


def test_converter_builds_expected_grid(tmp_path) -> None:
    source_path = tmp_path / "source.png"
    image = Image.new("RGB", (2, 1))
    image.putdata([(0, 0, 0), (255, 255, 255)])
    image.save(source_path)

    palette = [
        BeadColor("B", "黑", (0, 0, 0)),
        BeadColor("W", "白", (255, 255, 255)),
    ]
    project = BeadConverter(palette, "测试色板").convert(source_path, 2, 1, "stretch")

    assert project.width == 2
    assert project.height == 1
    assert project.grid == [["B", "W"]]
    assert project.color_counts() == {"B": 1, "W": 1}

