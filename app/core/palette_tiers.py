"""MARD 套装色卡等级及自动选择规则。"""

from __future__ import annotations

from app.core.project import BeadColor

PALETTE_LEVELS = (24, 48, 72, 96, 120, 221)

_TIER_24 = (
    "H2", "F5", "B8", "D7",
    "H1", "A6", "C3", "E2",
    "H3", "A7", "C5", "E4",
    "H4", "A4", "C8", "G1",
    "H5", "B3", "D9", "G5",
    "H7", "B5", "D6", "G7",
)

_ADD_48 = (
    "D19", "G9", "C7", "F8", "C2", "A11",
    "A13", "D18", "D13", "G13", "C6", "G8",
    "A10", "D21", "E8", "D3", "E7", "B12",
    "C10", "C11", "E3", "D15", "F13", "C13",
)

_ADD_72 = (
    "F7", "B17", "B19", "D2", "D20", "E13",
    "A3", "B20", "C16", "D19", "E1", "G2",
    "B14", "B10", "D8", "D12", "E12", "G3",
    "B18", "B7", "D11", "D14", "E5", "F10",
)

# 用户提供的 72/96/120 色商品图中 D19 同时出现在基础区和升级区。
# 这里保留图片原始格位；用于匹配时会按色号去重。

_ADD_96 = (
    "F12", "E9", "F2", "F9", "F3", "E6",
    "A14", "E10", "F4", "M5", "D16", "M6",
    "D5", "M9", "E11", "M12", "E15", "G17",
    "E14", "G14", "F14", "F6", "F1", "F11",
)

_ADD_120 = (
    "H12", "B15", "A5", "C1", "A9", "B6",
    "A1", "C14", "A15", "C4", "A8", "C15",
    "B13", "C9", "B16", "C17", "B1", "D17",
    "B2", "D1", "B4", "A12", "B11", "G6",
)

TIER_CODES: dict[int, tuple[str, ...]] = {
    24: _TIER_24,
    48: _TIER_24 + _ADD_48,
    72: _TIER_24 + _ADD_48 + _ADD_72,
    96: _TIER_24 + _ADD_48 + _ADD_72 + _ADD_96,
    120: _TIER_24 + _ADD_48 + _ADD_72 + _ADD_96 + _ADD_120,
}


def automatic_palette_level(width: int, height: int) -> int:
    """以短边 30、50、100 为自动分档边界。"""
    shortest_side = min(width, height)
    if shortest_side < 30:
        return 24
    if shortest_side < 50:
        return 48
    if shortest_side < 100:
        return 96
    return 221


def resolve_palette_level(requested_level: int, width: int, height: int) -> int:
    if requested_level == 0:
        return automatic_palette_level(width, height)
    if requested_level not in PALETTE_LEVELS:
        raise ValueError(f"不支持的色卡等级：{requested_level}")
    return requested_level


def colors_for_palette_level(
    palette: list[BeadColor] | tuple[BeadColor, ...],
    level: int,
) -> list[BeadColor]:
    """从完整色板中选出套装图片所列的精确色号。"""
    if level == 221:
        return list(palette)
    if level not in TIER_CODES:
        raise ValueError(f"不支持的色卡等级：{level}")

    colors_by_code = {color.code: color for color in palette}
    missing_codes = [code for code in TIER_CODES[level] if code not in colors_by_code]
    if missing_codes:
        raise ValueError(f"完整色板缺少 {level} 色套装色号：{', '.join(missing_codes)}")
    unique_codes = dict.fromkeys(TIER_CODES[level])
    return [colors_by_code[code] for code in unique_codes]
