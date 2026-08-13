from __future__ import annotations

from datetime import datetime
from pathlib import Path

import xlsxwriter
from xlsxwriter.utility import xl_col_to_name

from .model import Project, Task
from .palette import project_color_map, task_colors
from .timeline import Scale, buckets


def export_excel(
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
    book = xlsxwriter.Workbook(output)
    sheet = book.add_worksheet("Gantt")
    navy = "#18324A"
    title_fmt = book.add_format({"bold": True, "font_size": 18, "font_color": navy})
    subtitle_fmt = book.add_format({"font_size": 10, "font_color": "#526777"})
    head_fmt = book.add_format(
        {
            "bold": True,
            "font_color": "white",
            "bg_color": navy,
            "align": "center",
            "valign": "vcenter",
        }
    )
    date_fmt = book.add_format({"num_format": "yyyy-mm-dd", "font_color": "#243746"})
    pct_fmt = book.add_format({"num_format": "0%", "font_color": "#243746"})
    periods = buckets(scope_start or project.start, scope_finish or project.finish, scale)
    colors_by_root = project_color_map(tasks)
    fixed_headers = ["Outline", "Task", "Start", "Finish", "Progress"] + (
        ["Assignees"] if show_assignees else []
    )
    first_timeline_col = len(fixed_headers)
    last_col = first_timeline_col + len(periods) - 1
    sheet.merge_range(0, 0, 0, max(4, last_col), header or project.title or project.name, title_fmt)
    if subheader:
        sheet.merge_range(1, 0, 1, max(4, last_col), subheader, subtitle_fmt)
    metadata = []
    if show_generation_date:
        metadata.append(f"Generated: {datetime.now().astimezone().date().isoformat()}")
    if version:
        metadata.append(f"Version: {version}")
    if metadata:
        sheet.merge_range(2, 0, 2, max(4, last_col), " | ".join(metadata), subtitle_fmt)
    header_row = 4
    for col, value in enumerate(fixed_headers):
        sheet.write(header_row, col, value, head_fmt)
    timeline_head_fmt = book.add_format(
        {
            "bold": True,
            "font_color": "white",
            "bg_color": navy,
            "align": "center",
            "valign": "vcenter",
            "num_format": ("dd" if scale == "daily" else "dd mmm" if scale != "monthly" else "mmm"),
        }
    )
    hidden_date_fmt = book.add_format({"num_format": "yyyy-mm-dd"})
    for col, (period_start, period_end) in enumerate(periods, first_timeline_col):
        sheet.write_datetime(3, col, period_end, hidden_date_fmt)
        sheet.write_datetime(header_row, col, period_start, timeline_head_fmt)
        sheet.set_column(
            col,
            col,
            3 if scale == "daily" else 7 if scale in {"weekly", "fortnightly"} else 9,
        )
    sheet.set_row(3, None, None, {"hidden": True})

    for row_index, task in enumerate(tasks, header_row + 1):
        bar_color, row_color = task_colors(task, palette, colors_by_root)
        base = book.add_format(
            {
                "bold": task.summary,
                "bg_color": row_color if palette == "projects" or task.summary else "#FFFFFF",
                "font_color": "#18324A" if task.summary else "#243746",
            }
        )
        bar_fmt = book.add_format({"bg_color": bar_color, "border": 0})
        milestone_fmt = book.add_format({"font_color": bar_color, "bold": True, "align": "center"})
        sheet.set_row(row_index, 18, None, {"level": max(0, task.outline_level - 1)})
        sheet.write(row_index, 0, task.outline_number, base)
        sheet.write(row_index, 1, task.name, base)
        sheet.write_datetime(row_index, 2, task.start, date_fmt)
        sheet.write_datetime(row_index, 3, task.finish, date_fmt)
        sheet.write_number(row_index, 4, task.percent_complete / 100, pct_fmt)
        if show_assignees:
            sheet.write(row_index, 5, ", ".join(task.assignees), base)
        excel_row = row_index + 1
        for offset, _ in enumerate(periods):
            col = first_timeline_col + offset
            column = xl_col_to_name(col)
            if task.milestone:
                sheet.write_formula(
                    row_index,
                    col,
                    f'=IF(AND({column}$5<=$C{excel_row},{column}$4>$C{excel_row}),"◆","")',
                    milestone_fmt,
                    "",
                )
            else:
                sheet.write_blank(row_index, col, None)
        if not task.milestone:
            first = xl_col_to_name(first_timeline_col)
            sheet.conditional_format(
                row_index,
                first_timeline_col,
                row_index,
                last_col,
                {
                    "type": "formula",
                    "criteria": f"=AND({first}$5<=$D{excel_row},{first}$4>$C{excel_row})",
                    "format": bar_fmt,
                },
            )

    sheet.set_column(0, 0, 10)
    sheet.set_column(1, 1, 34)
    sheet.set_column(2, 3, 12)
    sheet.set_column(4, 4, 10)
    if show_assignees:
        sheet.set_column(5, 5, 24)
    sheet.freeze_panes(header_row + 1, first_timeline_col)
    sheet.autofilter(header_row, 0, header_row + len(tasks), last_col)
    sheet.hide_gridlines(2)
    sheet.set_landscape()
    sheet.set_paper(8 if paper == "a3" else 9)
    sheet.fit_to_pages(1, 0)
    sheet.repeat_rows(0, header_row)
    sheet.print_area(0, 0, header_row + len(tasks), last_col)
    sheet.set_margins(0.25, 0.25, 0.4, 0.4)
    sheet.set_header(f"&L{header or project.title or project.name}&RPage &P of &N")
    sheet.set_footer("&CGenerated by libre-gantt")
    sheet.set_tab_color(navy)
    book.close()
