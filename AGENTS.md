# Repository Guidelines

## Project Structure & Module Organization

Application code lives in `src/libre_gantt/`. `cli.py` defines the Typer command,
`parser.py` converts Microsoft Project XML into the Pydantic models in `model.py`,
and the PDF and Excel renderers are in `pdf_export.py` and `excel_export.py`.
Timeline bucketing and colour selection are isolated in `timeline.py` and
`palette.py`. Tests live in `tests/`; use `tests/fixtures/example-project.xml`
instead of relying on local exports. Generated PDFs, workbooks, and temporary
renders belong under `output/` or `tmp/` and should not be committed.

## Build, Test, and Development Commands

This project requires Python 3.14 and uses `uv` for dependency management.

- `uv sync --locked --all-groups` installs the exact runtime and development dependencies.
- `uv run libre-gantt export tests/fixtures/example-project.xml --format pdf` runs the CLI.
- `uv run pytest` executes the complete test suite.
- `uv run ruff check .` checks lint rules.
- `uv run ruff format --check .` verifies formatting; omit `--check` to format files.
- `uv run mypy` runs static analysis over `src/` as configured in `pyproject.toml`.
- `uv build` creates source and wheel distributions.

## Coding Style & Naming Conventions

Use four-space indentation, modern Python 3.14 type syntax, and type annotations
for every function. Ruff enforces a 100-character line length. Use `snake_case`
for functions, variables, and modules; `PascalCase` for Pydantic models and
enums; and uppercase names for constants. Keep parsing, layout calculations,
and format-specific rendering separate. Do not silence type errors globally;
scope exceptions to the untyped dependency that requires them.

## Testing Guidelines

Tests use pytest and follow `test_<behavior>` naming. Add compact, anonymized XML
fixtures under `tests/fixtures/`. Resolve fixtures relative to `__file__` so tests
also work when CI starts outside the repository root. Cover parser changes,
validation rules, timeline boundaries, and palette inheritance. For renderer
changes, generate a sample output and visually inspect its A3/A4 landscape layout.

## Commit & Pull Request Guidelines

History uses short, imperative subjects such as `Fix tests` and `Added palette`.
Prefer a specific present-tense subject, for example `Add monthly timeline labels`.
Keep commits focused. Pull requests should explain the user-visible change, list
verification commands, link relevant issues, and attach a screenshot or sample
render when PDF or Excel appearance changes. Ensure the locked sync, Ruff, mypy,
and pytest checks pass before requesting review.

## Security & Configuration

Do not commit customer project exports, assignee data, generated documents, or
virtual environments. Report security issues using the private contact in
`README.md` rather than the public issue tracker.
