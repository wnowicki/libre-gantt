from __future__ import annotations

from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A3, A4, landscape
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen.canvas import Canvas

from .model import Project, Task
from .palette import mix, project_color_map, task_colors
from .timeline import Scale, buckets, label

NAVY = colors.HexColor("#18324A")
BLUE = colors.HexColor("#2878B5")
PALE = colors.HexColor("#EAF2F8")
GRID = colors.HexColor("#CDD7E0")
TEXT = colors.HexColor("#243746")


def _clip(text: str, width: float, size: float) -> str:
    if stringWidth(text, "Helvetica", size) <= width:
        return text
    while text and stringWidth(text + "...", "Helvetica", size) > width:
        text = text[:-1]
    return text + "..."


def export_pdf(
    project: Project,
    tasks: list[Task],
    output: Path,
    paper: str,
    scale: Scale,
    header: str | None,
    subheader: str | None,
    show_generation_date: bool,
    version: str | None,
    show_assignees: bool,
    palette: str,
    scope_start: datetime | None = None,
    scope_finish: datetime | None = None,
) -> None:
    page_size = landscape(A3 if paper == "a3" else A4)
    width, height = page_size
    margin, title_h, timeline_h, footer_h, row_h = 28, 58, 32, 22, 18
    usable_h = height - 2 * margin - title_h - timeline_h - footer_h
    per_page = max(1, int(usable_h // row_h))
    canvas = Canvas(str(output), pagesize=page_size)
    periods = buckets(scope_start or project.start, scope_finish or project.finish, scale)
    colors_by_root = project_color_map(tasks)

    for page_start in range(0, len(tasks), per_page):
        page_tasks = tasks[page_start : page_start + per_page]
        title = header or project.title or project.name
        canvas.setFillColor(NAVY)
        canvas.setFont("Helvetica-Bold", 18)
        canvas.drawString(margin, height - margin - 16, title)
        canvas.setFont("Helvetica", 9)
        canvas.setFillColor(TEXT)
        if subheader:
            canvas.drawString(margin, height - margin - 32, subheader)
        meta = []
        if show_generation_date:
            meta.append(f"Generated: {datetime.now().astimezone().date().isoformat()}")
        if version:
            meta.append(f"Version: {version}")
        if meta:
            canvas.drawRightString(width - margin, height - margin - 16, "  |  ".join(meta))

        assignee_w = 92 if show_assignees else 0
        table_w = min(width * 0.46, 390) + assignee_w
        timeline_x = margin + table_w
        timeline_w = width - margin - timeline_x
        name_w = table_w - 142 - assignee_w
        cols = [("Task", name_w), ("Start", 52), ("Finish", 52), ("Done", 38)]
        if show_assignees:
            cols.append(("Assignees", assignee_w))
        y_top = height - margin - title_h
        canvas.setFillColor(NAVY)
        canvas.rect(margin, y_top - timeline_h, width - 2 * margin, timeline_h, fill=1, stroke=0)
        canvas.setFillColor(colors.white)
        canvas.setFont("Helvetica-Bold", 7)
        x: float = margin
        for caption, col_w in cols:
            canvas.drawString(x + 3, y_top - 20, caption)
            x += col_w
        cell_w = timeline_w / len(periods)
        for index, (period_start, _) in enumerate(periods):
            x = timeline_x + index * cell_w
            if cell_w >= 12 or index % max(1, int(18 / cell_w)) == 0:
                canvas.saveState()
                canvas.translate(x + cell_w / 2, y_top - 27)
                if cell_w < 20:
                    canvas.rotate(90)
                canvas.drawCentredString(0, 0, label(period_start, scale))
                canvas.restoreState()

        body_top = y_top - timeline_h
        for row, task in enumerate(page_tasks):
            y = body_top - (row + 1) * row_h
            bar_color, row_color = task_colors(task, palette, colors_by_root)
            if palette == "monochrome" and not task.summary and row % 2:
                row_color = "#F7F9FB"
            canvas.setFillColor(colors.HexColor(row_color))
            canvas.rect(margin, y, width - 2 * margin, row_h, fill=1, stroke=0)
            canvas.setStrokeColor(GRID)
            canvas.line(margin, y, width - margin, y)
            canvas.setFillColor(TEXT)
            canvas.setFont("Helvetica-Bold" if task.summary else "Helvetica", 7.5)
            indent = max(0, task.outline_level - 1) * 8
            canvas.drawString(
                margin + 3 + indent, y + 6, _clip(task.name, name_w - 7 - indent, 7.5)
            )
            x = margin + name_w
            canvas.setFont("Helvetica", 7)
            canvas.drawString(x + 3, y + 6, task.start.strftime("%Y-%m-%d"))
            x += 52
            canvas.drawString(x + 3, y + 6, task.finish.strftime("%Y-%m-%d"))
            x += 52
            canvas.drawRightString(x + 34, y + 6, f"{task.percent_complete}%")
            x += 38
            if show_assignees:
                canvas.drawString(x + 3, y + 6, _clip(", ".join(task.assignees), assignee_w - 6, 7))

            total = max(1.0, (periods[-1][1] - periods[0][0]).total_seconds())
            sx = (
                timeline_x
                + timeline_w
                * min(total, max(0, (task.start - periods[0][0]).total_seconds()))
                / total
            )
            ex = (
                timeline_x
                + timeline_w
                * min(total, max(0, (task.finish - periods[0][0]).total_seconds()))
                / total
            )
            cy = y + row_h / 2
            if task.milestone:
                canvas.setFillColor(colors.HexColor(bar_color))
                canvas.saveState()
                canvas.translate(sx, cy)
                canvas.rotate(45)
                canvas.rect(-4, -4, 8, 8, fill=1, stroke=0)
                canvas.restoreState()
            else:
                bar_h = 7 if not task.summary else 5
                canvas.setFillColor(colors.HexColor(bar_color))
                canvas.roundRect(sx, cy - bar_h / 2, max(2, ex - sx), bar_h, 2, fill=1, stroke=0)
                if task.percent_complete and not task.summary:
                    canvas.setFillColor(colors.HexColor(mix(bar_color, "#000000", 0.25)))
                    canvas.roundRect(
                        sx,
                        cy - bar_h / 2,
                        max(1, (ex - sx) * task.percent_complete / 100),
                        bar_h,
                        2,
                        fill=1,
                        stroke=0,
                    )

        canvas.setStrokeColor(GRID)
        for index in range(len(periods) + 1):
            x = timeline_x + index * cell_w
            canvas.line(x, body_top, x, body_top - len(page_tasks) * row_h)
        canvas.setFillColor(colors.HexColor("#607484"))
        canvas.setFont("Helvetica", 7)
        canvas.drawString(margin, margin, f"{project.name} | {scale.capitalize()} timeline")
        canvas.drawRightString(
            width - margin,
            margin,
            f"Page {page_start // per_page + 1} of {(len(tasks) + per_page - 1) // per_page}",
        )
        canvas.showPage()
    canvas.save()
