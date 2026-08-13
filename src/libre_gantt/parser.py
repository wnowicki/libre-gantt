from __future__ import annotations

from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET

from .model import Project, Task


def _text(node: ET.Element, name: str, default: str = "") -> str:
    child = node.find(f"{{*}}{name}")
    return child.text.strip() if child is not None and child.text else default


def _date(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def parse_project(path: Path) -> Project:
    root = ET.parse(path).getroot()
    resources = {
        int(_text(node, "UID", "0")): _text(node, "Name")
        for node in root.findall(".//{*}Resources/{*}Resource")
    }
    task_resources: dict[int, set[str]] = {}
    for assignment in root.findall(".//{*}Assignments/{*}Assignment"):
        task_uid = int(_text(assignment, "TaskUID", "0"))
        resource_name = resources.get(int(_text(assignment, "ResourceUID", "0")))
        if task_uid and resource_name:
            task_resources.setdefault(task_uid, set()).add(resource_name)

    tasks: list[Task] = []
    for node in root.findall(".//{*}Tasks/{*}Task"):
        uid = int(_text(node, "UID", "0"))
        start, finish = _text(node, "Start"), _text(node, "Finish")
        if not uid or not start or not finish:
            continue
        predecessors = [
            int(_text(link, "PredecessorUID", "0"))
            for link in node.findall("{*}PredecessorLink")
            if _text(link, "PredecessorUID", "0") != "0"
        ]
        tasks.append(
            Task(
                uid=uid,
                name=_text(node, "Name", f"Task {uid}"),
                outline_number=_text(node, "OutlineNumber"),
                outline_level=int(_text(node, "OutlineLevel", "1")),
                start=_date(start),
                finish=_date(finish),
                duration=_text(node, "Duration"),
                percent_complete=int(_text(node, "PercentComplete", "0")),
                summary=_text(node, "Summary", "0") == "1",
                milestone=_text(node, "Milestone", "0") == "1",
                predecessor_uids=predecessors,
                assignees=sorted(task_resources.get(uid, set())),
            )
        )
    if not tasks:
        raise ValueError("No dated tasks found in the XML file")
    return Project(
        name=_text(root, "Name", path.stem),
        title=_text(root, "Title", _text(root, "Name", path.stem)),
        manager=_text(root, "Manager"),
        start=_date(_text(root, "StartDate", min(t.start for t in tasks).isoformat())),
        finish=_date(
            _text(root, "FinishDate", max(t.finish for t in tasks).isoformat())
        ),
        tasks=tasks,
    )
