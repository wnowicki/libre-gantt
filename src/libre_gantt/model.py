from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class Task(Model):
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
    predecessor_uids: list[int] = Field(default_factory=list)
    assignees: list[str] = Field(default_factory=list)


class Project(Model):
    name: str
    title: str
    manager: str
    start: datetime
    finish: datetime
    tasks: list[Task]
