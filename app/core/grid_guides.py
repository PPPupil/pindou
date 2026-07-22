"""拼豆网格的五格分区与坐标标记规则。"""

from __future__ import annotations


GRID_GROUP_SIZE = 5


def coordinate_marks(length: int) -> tuple[int, ...]:
    """返回需要显示的坐标：第 1 格、每 5 格以及最后一格。"""
    if length <= 0:
        return ()
    marks = {1, length}
    marks.update(range(GRID_GROUP_SIZE, length + 1, GRID_GROUP_SIZE))
    return tuple(sorted(marks))


def is_major_grid_line(line_index: int, length: int) -> bool:
    """边界线和每五格分区线使用强调样式。"""
    return (
        line_index == 0
        or line_index == length
        or line_index % GRID_GROUP_SIZE == 0
    )
