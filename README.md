# GROMODEX

GROMODEX benchmarks GROMACS molecular dynamics performance with a deterministic full-factorial Design of Experiments (DOE). It can be used as a normal Python CLI or as a local MCP server so an agent can preview designs, generate CSVs, collect results, and launch controlled GROMACS runs.

## Project provenance

This repository is a refactored fork of the original GROMDEX project. The refactor of this fork, including the package layout, CLI/MCP interface, typing, testing, and development tooling, was carried out by Fabio Bove at NeoraLab.

The original scientific work and citation remain attributed to the authors listed in the Citation section.

## Project shape

GROMODEX is now a small source-layout package:

- `gromodex` CLI for local workflows.
- `gromodex-mcp` FastMCP server for agent use.
- Pydantic schemas for inputs and outputs.
- Standard-library DOE and CSV handling instead of `pyDOE3`, `numpy`, and `pandas`.
- Subprocess calls use argument lists, not `shell=True`.
- uv, ruff, mypy, pytest, pre-commit, and MkDocs configuration.

## Requirements

- Python 3.11 or newer
- [uv](https://docs.astral.sh/uv/)
- GROMACS available as `gmx` or via `--gmx-bin`
- NVIDIA GPU telemetry through `GPUtil` for GPU usage CSVs

## Install for development

```bash
uv sync --extra dev
```

## CLI usage

Preview the DOE:

```bash
uv run gromodex preview --gpu-count 2 --limit 5
```

Generate the design CSV:

```bash
uv run gromodex generate --gpu-count 2 --output gmx_fullfact_doe.csv
```

Run the full DOE:

```bash
uv run gromodex run \
  --workspace runs/example \
  --gpu-count 2 \
  --mdp input/md.mdp \
  --gro input/system.gro \
  --topology input/topol.top
```

Collect results from existing numbered run folders:

```bash
uv run gromodex collect \
  --workspace runs/example \
  --design runs/example/gmx_fullfact_doe.csv \
  --output runs/example/gmx_fullfact_doe_results.csv
```

## Agent CLI usage

Shell-capable agents can discover the CLI without MCP:

```bash
uv run gromodex tools
```

The command prints a JSON manifest with available commands, arguments, side effects, and a recommended workflow. All operational CLI commands also print JSON to stdout.

## MCP usage

Run over stdio, which is the safest local agent transport:

```bash
uv run gromodex-mcp --transport stdio
```

Example MCP command configuration:

```json
{
  "mcpServers": {
    "gromodex": {
      "command": "uv",
      "args": ["run", "gromodex-mcp", "--transport", "stdio"],
      "cwd": "/path/to/GROMODEX"
    }
  }
}
```

Available tools:

- `server_info`
- `preview_doe`
- `generate_doe`
- `collect_doe_results`
- `run_gromacs_doe`

## Documentation

Build the local docs site:

```bash
uv run mkdocs build --strict
```

## Development checks

```bash
uv run ruff format --check
uv run ruff check
uv run mypy
uv run pytest
uv run mkdocs build --strict
```

Install local pre-commit hooks:

```bash
uv run pre-commit install
```

## Citation

If you use GROMODEX in research or publications, cite:

GROMODEX: Optimisation of GROMACS Performance through a Design of Experiment Approach  
Marco Savioli, Paolo Calligari, Ugo Locatelli, Gianfranco Bocchinfuso  
bioRxiv 2025.10.08.681202; doi: https://doi.org/10.1101/2025.10.08.681202

## License

This project is released without a specific license. You are free to use, modify, and adapt it for research and educational purposes. If used in publications or derivative works, provide proper attribution to the authors.
