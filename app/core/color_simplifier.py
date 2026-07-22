"""低豆数作品的颜色数量限制与相邻近似色合并。"""

from __future__ import annotations

from collections import Counter, deque

from PIL import Image

from app.core.color_space import lab_distance_squared, rgb_to_lab
from app.core.project import BeadColor


def automatic_output_color_limit(width: int, height: int, image_style: str) -> int:
    """按豆数和图片类型选择实际使用颜色上限，而不是直接用完整色卡数量。"""
    short_side = min(width, height)
    if image_style == "cartoon":
        if short_side < 30:
            return 12
        if short_side < 50:
            return 16
        if short_side < 100:
            return 24
        return 32
    if short_side < 30:
        return 16
    if short_side < 50:
        return 24
    if short_side < 100:
        return 32
    return 48


def resolve_output_color_limit(
    requested_limit: int,
    width: int,
    height: int,
    image_style: str,
    available_colors: int,
) -> int:
    if available_colors < 1:
        raise ValueError("色板中没有可用颜色")
    if requested_limit < 0 or requested_limit == 1:
        raise ValueError("用色上限必须为 0（自动）或至少 2 色")
    resolved = requested_limit or automatic_output_color_limit(width, height, image_style)
    return max(1, min(resolved, available_colors))


def quantize_image(image: Image.Image, color_limit: int) -> Image.Image:
    """关闭抖动并把图像压缩到有限颜色，避免产生大量零散过渡色。"""
    return image.quantize(
        colors=color_limit,
        method=Image.Quantize.MEDIANCUT,
        dither=Image.Dither.NONE,
    ).convert("RGB")


def merge_similar_neighbors(
    grid: list[list[str]],
    palette: list[BeadColor] | tuple[BeadColor, ...],
    distance_threshold: float = 18,
    passes: int = 2,
) -> list[list[str]]:
    """把被相近主色包围的零散格子合并，保留色差明显的边缘。"""
    if not grid or not grid[0]:
        return grid

    lab_by_code = {color.code: rgb_to_lab(color.rgb) for color in palette}
    height = len(grid)
    width = len(grid[0])
    result = [row.copy() for row in grid]
    threshold_squared = distance_threshold**2

    for _ in range(passes):
        source = [row.copy() for row in result]
        changed = False
        for y in range(height):
            for x in range(width):
                neighbors = [
                    source[neighbor_y][neighbor_x]
                    for neighbor_y in range(max(0, y - 1), min(height, y + 2))
                    for neighbor_x in range(max(0, x - 1), min(width, x + 2))
                    if (neighbor_x, neighbor_y) != (x, y)
                ]
                if len(neighbors) < 2:
                    continue

                candidate, support = Counter(neighbors).most_common(1)[0]
                current = source[y][x]
                if candidate == current or support < 2:
                    continue
                if current not in lab_by_code or candidate not in lab_by_code:
                    continue

                distance_squared = lab_distance_squared(
                    lab_by_code[current],
                    lab_by_code[candidate],
                )
                if distance_squared <= threshold_squared:
                    result[y][x] = candidate
                    changed = True
        if not changed:
            break

    return result


def merge_small_regions(
    grid: list[list[str]],
    palette: list[BeadColor] | tuple[BeadColor, ...],
    max_region_size: int = 3,
    distance_threshold: float = 28,
    passes: int = 2,
) -> list[list[str]]:
    """合并 1～3 格的相近小色块；高色差轮廓不会被吞掉。"""
    if not grid or not grid[0] or max_region_size < 1:
        return grid

    lab_by_code = {color.code: rgb_to_lab(color.rgb) for color in palette}
    height = len(grid)
    width = len(grid[0])
    threshold_squared = distance_threshold**2
    result = [row.copy() for row in grid]

    for _ in range(passes):
        visited: set[tuple[int, int]] = set()
        changes: list[tuple[list[tuple[int, int]], str]] = []
        for start_y in range(height):
            for start_x in range(width):
                if (start_x, start_y) in visited:
                    continue
                current = result[start_y][start_x]
                region: list[tuple[int, int]] = []
                boundary: Counter[str] = Counter()
                queue = deque([(start_x, start_y)])
                visited.add((start_x, start_y))

                while queue:
                    x, y = queue.popleft()
                    region.append((x, y))
                    for neighbor_x, neighbor_y in (
                        (x - 1, y),
                        (x + 1, y),
                        (x, y - 1),
                        (x, y + 1),
                    ):
                        if not (0 <= neighbor_x < width and 0 <= neighbor_y < height):
                            continue
                        neighbor = result[neighbor_y][neighbor_x]
                        if neighbor == current:
                            if (neighbor_x, neighbor_y) not in visited:
                                visited.add((neighbor_x, neighbor_y))
                                queue.append((neighbor_x, neighbor_y))
                        else:
                            boundary[neighbor] += 1

                if len(region) > max_region_size or not boundary or current not in lab_by_code:
                    continue
                candidates = [
                    (code, shared_edges, lab_distance_squared(lab_by_code[current], lab_by_code[code]))
                    for code, shared_edges in boundary.items()
                    if shared_edges >= 2
                    and code in lab_by_code
                    and lab_distance_squared(lab_by_code[current], lab_by_code[code])
                    <= threshold_squared
                ]
                if candidates:
                    # 优先并入接触边最长的区域，同样长度时选择感知色差最近的颜色。
                    replacement = min(candidates, key=lambda item: (-item[1], item[2]))[0]
                    changes.append((region, replacement))

        if not changes:
            break
        for region, replacement in changes:
            for x, y in region:
                result[y][x] = replacement

    return result
