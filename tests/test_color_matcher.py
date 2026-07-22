from app.core.color_matcher import ColorMatcher
from app.core.project import BeadColor


def test_exact_color_is_matched() -> None:
    black = BeadColor("B", "黑", (0, 0, 0))
    white = BeadColor("W", "白", (255, 255, 255))
    matcher = ColorMatcher([black, white])

    assert matcher.find_nearest((0, 0, 0)) == black
    assert matcher.find_nearest((250, 250, 250)) == white

