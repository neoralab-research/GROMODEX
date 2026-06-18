# Development

Install dependencies:

```bash
uv sync --extra dev
```

Run checks:

```bash
uv run ruff format --check
uv run ruff check
uv run mypy
uv run pytest
uv run mkdocs build --strict
```

Install pre-commit hooks:

```bash
uv run pre-commit install
```

The package uses a `src/` layout. Keep business logic in reusable modules and keep CLI or MCP functions thin.

Keep `CHANGELOG.md` as the single changelog source instead of duplicating release notes under `docs/`.
