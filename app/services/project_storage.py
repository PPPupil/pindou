"""保存和读取 JSON 格式的拼豆工程。"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from app.core.project import BeadProject


def save_project(project: BeadProject, path: str | Path) -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8") as file:
        json.dump(asdict(project), file, ensure_ascii=False, indent=2)
    return destination


def load_project(path: str | Path) -> BeadProject:
    with Path(path).open("r", encoding="utf-8") as file:
        data = json.load(file)
    return BeadProject(**data)

