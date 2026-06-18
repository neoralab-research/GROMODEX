"""Command line interface for GROMODEX."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, cast

from gromodex.agent import agent_manifest
from gromodex.design import generate_design, summarize_design, write_design_csv
from gromodex.runner import collect_results_from_csv, run_doe
from gromodex.schemas import GPUCount, GromacsInputFiles, GromodexRunSettings
from gromodex.version import __version__


def _json_dump(value: Any) -> str:
    """Serialize Pydantic-compatible values to stable JSON."""
    if hasattr(value, "model_dump"):
        value = value.model_dump(mode="json")
    return json.dumps(value, indent=2, sort_keys=True)


def _gpu_count(value: str) -> GPUCount:
    """Parse a supported GPU count for argparse."""
    parsed = int(value)
    if parsed not in {2, 3, 4}:
        raise argparse.ArgumentTypeError("GPU count must be one of 2, 3, or 4")
    return cast(GPUCount, parsed)


def build_parser() -> argparse.ArgumentParser:
    """Build the top-level CLI parser.

    Returns:
        Configured argument parser.
    """
    parser = argparse.ArgumentParser(description="GROMODEX DOE and MCP utilities")
    parser.add_argument("--version", action="version", version=f"GROMODEX {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("tools", help="Print the agent-facing CLI tool manifest")

    preview = subparsers.add_parser("preview", help="Preview the generated DOE")
    preview.add_argument("--gpu-count", type=_gpu_count, default=2)
    preview.add_argument("--limit", type=int, default=10)

    generate = subparsers.add_parser("generate", help="Generate the DOE CSV")
    generate.add_argument("--gpu-count", type=_gpu_count, default=2)
    generate.add_argument("--output", type=Path, default=Path("gmx_fullfact_doe.csv"))

    collect = subparsers.add_parser("collect", help="Collect results from run directories")
    collect.add_argument("--workspace", type=Path, default=Path())
    collect.add_argument("--design", type=Path, default=Path("gmx_fullfact_doe.csv"))
    collect.add_argument("--output", type=Path, default=Path("gmx_fullfact_doe_results.csv"))
    collect.add_argument("--deffnm", default="md")

    run = subparsers.add_parser("run", help="Run the complete GROMACS DOE")
    run.add_argument("--workspace", type=Path, default=Path())
    run.add_argument("--gpu-count", type=_gpu_count, default=2)
    run.add_argument("--mdp", type=Path, required=True)
    run.add_argument("--gro", type=Path, required=True)
    run.add_argument("--topology", type=Path, required=True)
    run.add_argument("--gmx-bin", default="gmx")
    run.add_argument("--deffnm", default="md")
    run.add_argument("--nsteps", type=int, default=25_000)
    run.add_argument("--npme", type=int, default=1)
    run.add_argument("--maxwarn", type=int, default=2)
    run.add_argument("--monitoring-interval-seconds", type=float, default=1.0)
    run.add_argument("--timeout-seconds", type=int, default=None)
    run.add_argument("--keep-intermediate-files", action="store_true")

    return parser


def main(argv: list[str] | None = None) -> None:
    """Run the command line interface.

    Args:
        argv: Optional argument list for tests or programmatic use.
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "tools":
        print(_json_dump(agent_manifest()))
        return

    if args.command == "preview":
        print(_json_dump(summarize_design(args.gpu_count, args.limit)))
        return

    if args.command == "generate":
        design = generate_design(args.gpu_count)
        output_path = write_design_csv(design, args.output)
        summary = summarize_design(args.gpu_count, preview_limit=5)
        summary.output_path = output_path
        print(_json_dump(summary))
        return

    if args.command == "collect":
        collect_summary = collect_results_from_csv(
            args.workspace,
            args.design,
            args.output,
            deffnm=args.deffnm,
        )
        print(_json_dump(collect_summary))
        return

    if args.command == "run":
        settings = GromodexRunSettings(
            workspace=args.workspace,
            input_files=GromacsInputFiles(mdp=args.mdp, gro=args.gro, topology=args.topology),
            gpu_count=args.gpu_count,
            gmx_bin=args.gmx_bin,
            deffnm=args.deffnm,
            nsteps=args.nsteps,
            npme=args.npme,
            maxwarn=args.maxwarn,
            monitoring_interval_seconds=args.monitoring_interval_seconds,
            timeout_seconds=args.timeout_seconds,
            keep_intermediate_files=args.keep_intermediate_files,
        )
        print(_json_dump(run_doe(settings)))
        return

    parser.error(f"Unhandled command: {args.command}")
