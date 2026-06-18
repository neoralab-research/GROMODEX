# Agent CLI

GROMODEX does not require MCP when an agent can run shell commands. The package CLI prints JSON for every operational command and exposes a machine-readable manifest:

```bash
uv run gromodex tools
```

Use this mode for agents that can execute commands but do not support MCP server registration.

## Command contract

- `preview` is read-only and returns DOE metadata plus preview rows.
- `generate` writes a deterministic design CSV.
- `collect` reads numbered run folders and writes a results CSV.
- `run` executes GROMACS, monitors GPU usage, and writes workspace outputs.

The `run` command should be launched only after the agent has explicit paths for `--mdp`, `--gro`, `--topology`, and `--workspace`.

## Discovery output

The manifest includes command examples, argument metadata, output format, and side-effect notes. Agents should inspect it before choosing a command:

```bash
uv run gromodex tools
```

## Recommended sequence

```bash
uv run gromodex preview --gpu-count 2 --limit 5
uv run gromodex generate --gpu-count 2 --output gmx_fullfact_doe.csv
uv run gromodex run \
  --workspace runs/example \
  --gpu-count 2 \
  --mdp input/md.mdp \
  --gro input/system.gro \
  --topology input/topol.top
uv run gromodex collect \
  --workspace runs/example \
  --design runs/example/gmx_fullfact_doe.csv \
  --output runs/example/gmx_fullfact_doe_results.csv
```
