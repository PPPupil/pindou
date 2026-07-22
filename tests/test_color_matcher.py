from app.core.color_matcher import ColorMatcher
from app.core.project import BeadColor


def test_exact_color_is_matched() -> None:
    black = BeadColor("B", "黑", (0, 0, 0))
    white = BeadColor("W", "白", (255, 255, 255))
    matcher = ColorMatcher([black, white])

    assert matcher.find_nearest((0, 0, 0)) == black
    assert matcher.find_nearest((250, 250, 250)) == white


def test_transparent_color_is_not_used_for_opaque_image_matching() -> None:
    transparent_white = BeadColor(
        "H1", "透明", (252, 252, 252), transparent=True
    )
    opaque_white = BeadColor("H2", "白", (249, 249, 249))

    matcher = ColorMatcher([transparent_white, opaque_white])

    assert matcher.find_nearest((255, 255, 255)).code == "H2"

