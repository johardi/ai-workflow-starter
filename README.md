# LinkML Editor

A browser-based visual form builder for creating [LinkML](https://linkml.io/) schemas — without writing code.

## Features

- Visual three-panel builder (palette, canvas, config)
- Typed fields with configurable constraints
- Enum management with permissible values
- Drag-and-drop field ordering
- Auto-saving configuration
- One-click LinkML YAML export with validation
- Live form preview

## Quick Start

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/johardi/ai-workflow-starter
cd ai-workflow-starter

uv sync
uv run python manage.py migrate
uv run python manage.py runserver
```

Open [http://localhost:8000](http://localhost:8000).

## Project Structure

```
linkml-editor/
├── builder/               # Main Django app
│   ├── models.py          # FormTemplate, FormSection, FormField, EnumDefinition
│   ├── views.py           # HTMX-aware class-based views
│   ├── forms.py           # ModelForms and formsets
│   ├── services/          # LinkML builder and exporter
│   ├── templates/builder/ # Django templates (base + HTMX partials)
│   └── static/builder/    # CSS (Studio Theme) and JS (SortableJS)
├── config/                # Django settings
└── pyproject.toml         # Python project config
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Make your changes
4. Run the dev server and verify manually at `localhost:8000`
5. Format code: `uvx ruff format .`
6. Commit your changes (`git commit -m "Add my feature"`)
7. Push to your branch (`git push origin feature/my-feature`)
8. Open a Pull Request

### Guidelines

- Follow existing patterns: HTMX partials for server responses, Alpine.js for client state
- Keep templates in `builder/templates/builder/partials/` for HTMX-swapped fragments
- Use the Studio Theme conventions (stone colors, DM Sans font, emerald accents) for new UI
- Read `CLAUDE.md` for architecture context and common patterns

## License

[MIT](LICENSE)
