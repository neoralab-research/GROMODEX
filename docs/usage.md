# Usage

## Generate a design

```bash
uv run gromodex generate --gpu-count 2 --output gmx_fullfact_doe.csv
```

Supported GPU counts are 2, 3, and 4.

## Run GROMACS DOE

```bash
uv run gromodex run \
  --workspace runs/example \
  --gpu-count 2 \
  --mdp input/md.mdp \
  --gro input/system.gro \
  --topology input/topol.top
```

The run command writes:

- `gmx_fullfact_doe.csv`
- numbered run directories such as `1/` and `2/`
- `gpu_usage_runX.csv` files
- `<deffnm>.log` files, where `deffnm` defaults to `md`
- `gmx_fullfact_doe_results.csv`
- `doe.log`

## Collect existing results

```bash
uv run gromodex collect \
  --workspace runs/example \
  --design runs/example/gmx_fullfact_doe.csv \
  --output runs/example/gmx_fullfact_doe_results.csv
```

Collection is useful when runs were launched manually or resumed outside GROMODEX. Pass `--deffnm <name>` if the run logs are named something other than `md.log`.
