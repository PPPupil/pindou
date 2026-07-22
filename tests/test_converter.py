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


def test_converter_preserves_ratio_and_pads_with_white(tmp_path) -> None:
    source_path = tmp_path / "wide.png"
    Image.new("RGB", (4, 2), (0, 0, 0)).save(source_path)
    palette = [
        BeadColor("B", "黑", (0, 0, 0)),
        BeadColor("W", "白", (255, 255, 255)),
    ]

    project = BeadConverter(palette).convert(source_path, 4, 4, "contain")

    assert project.grid[0] == ["W", "W", "W", "W"]
    assert project.grid[1] == ["B", "B", "B", "B"]
    assert project.grid[2] == ["B", "B", "B", "B"]
    assert project.grid[3] == ["W", "W", "W", "W"]


def test_converter_honors_independent_output_color_limit(tmp_path) -> None:
    source_path = tmp_path / "gradient.png"
    image = Image.new("RGB", (40, 40))
    image.putdata(
        [
            (x * 255 // 39, y * 255 // 39, (x + y) * 255 // 78)
            for y in range(40)
            for x in range(40)
        ]
    )
    image.save(source_path)
    palette = [
        BeadColor(f"C{index}", f"灰{index}", (index, index, index))
        for index in range(0, 256, 8)
    ]

    project = BeadConverter(palette).convert(
        source_path,
        40,
        40,
        "stretch",
        221,
        "cartoon",
        12,
    )

    assert project.image_style == "cartoon"
    assert project.color_limit == 12
    assert len(project.color_counts()) <= 12


def test_cartoon_near_black_outline_prefers_black_bead(tmp_path) -> None:
    source_path = tmp_path / "dark-green-line.png"
    Image.new("RGB", (8, 8), (47, 55, 47)).save(source_path)
    palette = [
        BeadColor("H7", "黑色", (32, 32, 31)),
        BeadColor("B23", "深绿色", (47, 55, 47)),
        BeadColor("H2", "白色", (250, 250, 248)),
    ]

    project = BeadConverter(palette).convert(
        source_path,
        2,
        2,
        "stretch",
        221,
        "cartoon",
        3,
    )

    assert project.grid == [["H7", "H7"], ["H7", "H7"]]
