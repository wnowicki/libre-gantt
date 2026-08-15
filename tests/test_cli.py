from __future__ import annotations

import re
from pathlib import Path
from unittest.mock import Mock

import pytest
from typer.testing import CliRunner

from libre_gantt.cli import app

FIXTURE = Path(__file__).parent / "fixtures" / "example-project.xml"


def test_export_passes_date_scope_and_filters_tasks(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    exporter = Mock()
    monkeypatch.setattr("libre_gantt.cli.export_pdf", exporter)
    output = tmp_path / "scoped.pdf"

    result = CliRunner().invoke(
        app,
        [
            "export",
            str(FIXTURE),
            "--output",
            str(output),
            "--start-date",
            "2026-02-01",
            "--end-date",
            "2026-02-28",
        ],
    )

    assert result.exit_code == 0
    args = exporter.call_args.args
    assert args[-2].isoformat() == "2026-02-01T00:00:00"
    assert args[-1].date().isoformat() == "2026-02-28"
    assert all(task.start <= args[-1] and task.finish >= args[-2] for task in args[1])


def test_export_rejects_reversed_date_scope(tmp_path: Path) -> None:
    result = CliRunner().invoke(
        app,
        [
            "export",
            str(FIXTURE),
            "--output",
            str(tmp_path / "scoped.pdf"),
            "--start-date",
            "2026-03-01",
            "--end-date",
            "2026-02-01",
        ],
        color=False,
    )

    assert result.exit_code == 2
    plain_output = re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", result.output)
    assert "--start-date must be on or before --end-date" in plain_output
