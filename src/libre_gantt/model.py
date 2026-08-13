from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class Task:
    uid: int
    name: str
    outline_number: str
    outline_level: int
    start: datetime
    finish: datetime
    duration: str
    percent_complete: int
    summary: bool
    milestone: bool
    predecessor_uids: list[int] = field(default_factory=list)
    assignees: list[str] = field(default_factory=list)


@dataclass(slots=True)
class Project:
    name: str
    title: str
    manager: str
    start: datetime
    finish: datetime
    tasks: list[Task]
