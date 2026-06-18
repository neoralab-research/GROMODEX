# AGENTS.md

GROMODEX can be used by shell-capable agents without MCP through its JSON CLI.

## Discover Tools

```bash
uv run gromodex tools
```

The command prints a JSON manifest with available commands, arguments, side effects, and a recommended workflow.

## Safe Workflow

1. Preview before writing files:

```bash
uv run gromodex preview --gpu-count 2 --limit 5
```

2. Generate a DOE CSV only after the preview looks correct:

```bash
uv run gromodex generate --gpu-count 2 --output gmx_fullfact_doe.csv
```

3. Run simulations only when MDP, GRO, topology, GPU count, and workspace are explicit:

```bash
uv run gromodex run \
  --workspace runs/example \
  --gpu-count 2 \
  --mdp input/md.mdp \
  --gro input/system.gro \
  --topology input/topol.top
```

4. Collect existing results with the matching `deffnm` log stem:

```bash
uv run gromodex collect \
  --workspace runs/example \
  --design runs/example/gmx_fullfact_doe.csv \
  --output runs/example/gmx_fullfact_doe_results.csv
```

Do not run `gromodex run` unless GROMACS is installed and the user has confirmed that launching the DOE is intended.
