from PIL import Image

from app.core.image_processor import detect_image_style, load_and_resize


def test_cartoon_resize_does_not_create_lanczos_transition_colors(tmp_path) -> None:
    source_path = tmp_path / "hard-edge.png"
    image = Image.new("RGB", (2, 1))
    image.putdata([(0, 0, 0), (255, 255, 255)])
    image.save(source_path)

    cartoon = load_and_resize(
        source_path,
        (20, 1),
        "stretch",
        image_style="cartoon",
    )
    photo = load_and_resize(
        source_path,
        (20, 1),
        "stretch",
        image_style="photo",
    )

    assert set(cartoon.get_flattened_data()) == {(0, 0, 0), (255, 255, 255)}
    assert len(set(photo.get_flattened_data())) > 2


def test_flat_color_image_is_detected_as_cartoon(tmp_path) -> None:
    source_path = tmp_path / "flat.png"
    image = Image.new("RGB", (64, 64), (245, 205, 175))
    for coordinate in range(64):
        image.putpixel((coordinate, coordinate), (50, 35, 35))
    image.save(source_path)

    assert detect_image_style(source_path) == "cartoon"


def test_cartoon_sampling_keeps_black_line_and_discards_gray_halo(tmp_path) -> None:
    source_path = tmp_path / "outlined.png"
    background = (245, 210, 220)
    image = Image.new("RGB", (12, 4), background)
    # 中间目标格包含真正黑线，右侧目标格只有少量抗锯齿灰边。
    for y in range(4):
        image.putpixel((4, y), (35, 35, 35))
        image.putpixel((5, y), (120, 115, 118))
        image.putpixel((8, y), (175, 160, 165))
    image.save(source_path)

    result = load_and_resize(
        source_path,
        (3, 1),
        "stretch",
        image_style="cartoon",
        color_limit=4,
    )

    pixels = list(result.get_flattened_data())
    assert pixels[1] == (0, 0, 0)
    assert pixels[2] == pixels[0]
