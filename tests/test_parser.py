from pathlib import Path

from libre_gantt.parser import parse_project
from libre_gantt.timeline import buckets


def test_parse_sample_project() -> None:
    project = parse_project(Path("project.xml"))
    assert project.name == "IamIP"
    assert len(project.tasks) == 36
    assert project.tasks[0].summary
    assert project.tasks[1].outline_level == 2
    assert project.tasks[2].predecessor_uids == [2]
    assert sum(bool(task.assignees) for task in project.tasks) > 0


def test_timeline_buckets_cover_project() -> None:
    project = parse_project(Path("project.xml"))
    weekly = buckets(project.start, project.finish, "weekly")
    monthly = buckets(project.start, project.finish, "monthly")
    assert len(weekly) > len(monthly)
    assert weekly[0][0] <= project.start < weekly[-1][1]
