# Libre Gantt Generator

Generate a polished, landscape PDF or an editable Excel Gantt chart from the
Microsoft Project XML exported by ProjectLibre.

Requires Python 3.14 or newer. `uv` selects the version declared in
`.python-version` automatically.

## Run

```bash
uv run libre-gantt export project.xml --format pdf --paper a3 --timeline weekly
```

Create an editable workbook with all subtasks and assignees:

```bash
uv run libre-gantt export project.xml \
  --format excel \
  --output project-gantt.xlsx \
  --paper a3 \
  --timeline weekly \
  --detail all \
  --assignees \
  --header "Product delivery plan" \
  --subheader "Engineering portfolio" \
  --generation-date \
  --version date
```

Create an A4 executive PDF containing only outline-level-one tasks:

```bash
uv run libre-gantt export project.xml \
  --format pdf --paper a4 --timeline monthly --detail top \
  --header "Portfolio roadmap" --version "v1.0"
```

Available timeline scales are `daily`, `weekly`, and `monthly`. PDF output is
always landscape. Excel output includes landscape print settings, repeating
headers, frozen task columns, filters, outline levels, and a one-page-wide
print area. If `--output` is omitted, the result is written next to the XML as
`<name>-gantt.pdf` or `<name>-gantt.xlsx`.

## Security

If you discover any security-related issues, please email [email](mailto:wnowicki@me.com) instead of using the issue tracker.

## License

This project is licensed under the [MIT License](LICENSE).

---
Copyright (c) 2026 [Wojciech Nowicki](wnowicki.dev)
