# MCP

Start the server with stdio transport:

```bash
uv run gromodex-mcp --transport stdio
```

For local HTTP transport:

```bash
uv run gromodex-mcp --transport streamable-http --host 127.0.0.1 --port 8000 --path /mcp
```

## Tools

### `server_info`

Returns version, available tools, and safety characteristics.

### `preview_doe`

Returns row count, factors, and a preview of the DOE for 2, 3, or 4 GPUs.

### `generate_doe`

Writes the design CSV and returns a structured summary.

### `collect_doe_results`

Reads numbered run folders and writes a results CSV with `Performance (ns/day)`. Use the `deffnm` argument when log files are named something other than `md.log`.

### `run_gromacs_doe`

Runs the full workflow from MDP, GRO, and topology files. The tool validates primitive MCP arguments with Pydantic before invoking GROMACS.
