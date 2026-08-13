from __future__ import annotations

from .model import Task

PROJECT_COLORS = (
    "#2878B5",
    "#D95F59",
    "#2D9D78",
    "#8B6BB1",
    "#D18832",
    "#3E8E9E",
    "#C05A8A",
    "#6F8F3D",
    "#5969C2",
    "#A66A45",
)


def mix(hex_color: str, target: str = "#FFFFFF", amount: float = 0.5) -> str:
    source = tuple(int(hex_color[i : i + 2], 16) for i in (1, 3, 5))
    destination = tuple(int(target[i : i + 2], 16) for i in (1, 3, 5))
    values = (round(a + (b - a) * amount) for a, b in zip(source, destination, strict=True))
    return "#" + "".join(f"{value:02X}" for value in values)


def project_color_map(tasks: list[Task]) -> dict[str, str]:
    roots = list(
        dict.fromkeys(task.outline_number.split(".", 1)[0] or str(task.uid) for task in tasks)
    )
    return {root: PROJECT_COLORS[index % len(PROJECT_COLORS)] for index, root in enumerate(roots)}


def task_colors(task: Task, palette: str, colors_by_root: dict[str, str]) -> tuple[str, str]:
    if palette == "monochrome":
        return (
            "#18324A" if task.summary else "#2878B5",
            "#EAF2F8" if task.summary else "#FFFFFF",
        )
    root = task.outline_number.split(".", 1)[0] or str(task.uid)
    base = colors_by_root[root]
    depth = max(0, task.outline_level - 1)
    return mix(base, amount=min(0.58, depth * 0.28)), mix(base, amount=0.86 if depth == 0 else 0.94)
