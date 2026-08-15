from __future__ import annotations

from datetime import datetime, time
from enum import Enum
from pathlib import Path
from typing import Annotated

import typer

from .excel_export import export_excel
from .parser import parse_project
from .pdf_export import export_pdf

app = typer.Typer(
    no_args_is_help=True,
    help="Create printable Gantt charts from Microsoft Project XML.",
)


@app.callback()
def main() -> None:
    """Create printable Gantt charts from Microsoft Project XML."""


class OutputFormat(str, Enum):
    pdf = "pdf"
    excel = "excel"


class Paper(str, Enum):
    a3 = "a3"
    a4 = "a4"


class Timeline(str, Enum):
    daily = "daily"
    weekly = "weekly"
    fortnightly = "fortnightly"
    monthly = "monthly"


class Detail(str, Enum):
    top = "top"
    all = "all"


class Palette(str, Enum):
    monochrome = "monochrome"
    projects = "projects"


@app.command()
def export(
    input_file: Annotated[
        Path,
        typer.Argument(
            exists=True,
            dir_okay=False,
            readable=True,
            help="Microsoft Project XML file",
        ),
    ],
    output: Annotated[
        Path | None, typer.Option("--output", "-o", help="Output .pdf or .xlsx path")
    ] = None,
    format: Annotated[OutputFormat, typer.Option("--format", "-f")] = OutputFormat.pdf,
    paper: Annotated[Paper, typer.Option(help="Landscape paper size")] = Paper.a3,
    timeline: Annotated[Timeline, typer.Option(help="Timeline column scale")] = Timeline.weekly,
    start_date: Annotated[
        datetime | None,
        typer.Option(
            formats=["%Y-%m-%d"], help="First date to include in the timeline (YYYY-MM-DD)"
        ),
    ] = None,
    end_date: Annotated[
        datetime | None,
        typer.Option(
            formats=["%Y-%m-%d"], help="Last date to include in the timeline (YYYY-MM-DD)"
        ),
    ] = None,
    detail: Annotated[
        Detail, typer.Option(help="Top-level tasks only or all subtasks")
    ] = Detail.all,
    palette: Annotated[
        Palette, typer.Option(help="Colour treatment for project bars")
    ] = Palette.projects,
    assignees: Annotated[
        bool,
        typer.Option("--assignees/--no-assignees", help="Include assignees in detailed view"),
    ] = False,
    header: Annotated[
        str | None, typer.Option(help="Document title; defaults to project title")
    ] = None,
    subheader: Annotated[str | None, typer.Option(help="Optional document subtitle")] = None,
    generation_date: Annotated[
        bool,
        typer.Option("--generation-date/--no-generation-date", help="Show generation date"),
    ] = True,
    version: Annotated[
        str | None, typer.Option(help="Version label; use 'date' for today's date")
    ] = None,
) -> None:
    """Export a ProjectLibre/Microsoft Project XML schedule."""
    project = parse_project(input_file)
    scope_start = datetime.combine(start_date.date(), time.min) if start_date else project.start
    scope_finish = datetime.combine(end_date.date(), time.max) if end_date else project.finish
    if scope_start > scope_finish:
        raise typer.BadParameter("--start-date must be on or before --end-date")
    tasks = (
        project.tasks
        if detail is Detail.all
        else [task for task in project.tasks if task.outline_level == 1]
    )
    tasks = [task for task in tasks if task.start <= scope_finish and task.finish >= scope_start]
    if not tasks:
        raise typer.BadParameter("The selected detail level and date scope contain no tasks")
    if assignees and detail is Detail.top:
        typer.echo(
            "Note: assignees are only shown in detailed view; ignoring --assignees.",
            err=True,
        )
        assignees = False
    resolved_version = (
        datetime.now().astimezone().date().isoformat() if version == "date" else version
    )
    suffix = ".pdf" if format is OutputFormat.pdf else ".xlsx"
    destination = output or input_file.with_name(f"{input_file.stem}-gantt{suffix}")
    if destination.suffix.lower() != suffix:
        raise typer.BadParameter(f"Output for {format.value} must use the {suffix} extension")
    destination.parent.mkdir(parents=True, exist_ok=True)
    exporter = export_pdf if format is OutputFormat.pdf else export_excel
    exporter(
        project,
        tasks,
        destination,
        paper.value,
        timeline.value,
        header,
        subheader,
        generation_date,
        resolved_version,
        assignees,
        palette.value,
        scope_start,
        scope_finish,
    )
    typer.echo(f"Created {destination}")


if __name__ == "__main__":
    app()
