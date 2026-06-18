"""MCP tool surface for GROMODEX."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Any, cast

from mcp.server.fastmcp import FastMCP

from gromodex.design import generate_design, summarize_design, write_design_csv
from gromodex.runner import collect_results_from_csv, run_doe
from gromodex.schemas import GPUCount, GromacsInputFiles, GromodexRunSettings
from gromodex.version import __version__

mcp = FastMCP(
    "gromodex",
    host=os.getenv("GROMODEX_MCP_HOST", "127.0.0.1"),
    port=int(os.getenv("GROMODEX_MCP_PORT", "8000")),
)


def _validated_gpu_count(value: int) -> GPUCount:
    """Validate a GPU count from MCP primitive arguments."""
    if value not in {2, 3, 4}:
        msg = "gpu_count must be one of 2, 3, or 4"
        raise ValueError(msg)
    return cast(GPUCount, value)


def _dump(value: Any) -> dict[str, Any]:
    """Return a JSON-compatible dict from a Pydantic model."""
    if hasattr(value, "model_dump"):
        return cast(dict[str, Any], value.model_dump(mode="json"))
    return dict(value)


@mcp.tool()
def server_info() -> dict[str, Any]:
    """Return GROMODEX MCP runtime information."""
    return {
        "name": "gromodex",
        "version": __version__,
        "tools": [
            "preview_doe",
            "generate_doe",
            "collect_doe_results",
            "run_gromacs_doe",
        ],
        "safety": {
            "shell_invocation": False,
            "validated_pydantic_inputs": True,
            "deterministic_factorial_design": True,
        },
    }


@mcp.tool()
def preview_doe(gpu_count: int = 2, limit: int = 10) -> dict[str, Any]:
    """Preview the full-factorial GROMACS design.

    Args:
        gpu_count: Number of GPUs to target. Supported values are 2, 3, and 4.
        limit: Maximum number of design rows to return.

    Returns:
        Design summary with preview rows.
    """
    summary = summarize_design(_validated_gpu_count(gpu_count), preview_limit=limit)
    return _dump(summary)


@mcp.tool()
def generate_doe(gpu_count: int = 2, output_path: str = "gmx_fullfact_doe.csv") -> dict[str, Any]:
    """Generate a DOE CSV for agent-led review or execution.

    Args:
        gpu_count: Number of GPUs to target. Supported values are 2, 3, and 4.
        output_path: CSV destination.

    Returns:
        Design summary including the written path.
    """
    validated_gpu_count = _validated_gpu_count(gpu_count)
    design = generate_design(validated_gpu_count)
    written_path = write_design_csv(design, Path(output_path))
    summary = summarize_design(validated_gpu_count, preview_limit=5)
    summary.output_path = written_path
    return _dump(summary)


@mcp.tool()
def collect_doe_results(
    workspace: str = ".",
    design_path: str = "gmx_fullfact_doe.csv",
    output_path: str = "gmx_fullfact_doe_results.csv",
    deffnm: str = "md",
) -> dict[str, Any]:
    """Collect GROMACS performance values from numbered DOE directories.

    Args:
        workspace: Directory containing ``1/``, ``2/``, and subsequent run folders.
        design_path: CSV design file used to map runs to factors.
        output_path: Destination results CSV.
        deffnm: GROMACS ``-deffnm`` file stem used for run logs.

    Returns:
        Collection summary and per-run metrics.
    """
    return _dump(
        collect_results_from_csv(
            Path(workspace),
            Path(design_path),
            Path(output_path),
            deffnm=deffnm,
        )
    )


@mcp.tool()
def run_gromacs_doe(
    mdp_file: str,
    gro_file: str,
    topology_file: str,
    workspace: str = ".",
    gpu_count: int = 2,
    gmx_bin: str = "gmx",
    deffnm: str = "md",
    nsteps: int = 25_000,
    npme: int = 1,
    maxwarn: int = 2,
    monitoring_interval_seconds: float = 1.0,
    keep_intermediate_files: bool = False,
    timeout_seconds: int | None = None,
) -> dict[str, Any]:
    """Run the complete GROMACS DOE and return structured results.

    Args:
        mdp_file: MDP parameter file.
        gro_file: Coordinate file.
        topology_file: Topology file.
        workspace: Output workspace for generated files and run directories.
        gpu_count: Number of GPUs to target. Supported values are 2, 3, and 4.
        gmx_bin: GROMACS executable.
        deffnm: GROMACS ``-deffnm`` file stem.
        nsteps: Number of MD steps per run.
        npme: Number of PME ranks.
        maxwarn: ``gmx grompp -maxwarn`` value.
        monitoring_interval_seconds: GPU polling interval.
        keep_intermediate_files: Keep all GROMACS outputs in each run directory.
        timeout_seconds: Optional timeout per subprocess.

    Returns:
        Structured DOE execution summary.
    """
    settings = GromodexRunSettings(
        workspace=Path(workspace),
        input_files=GromacsInputFiles(
            mdp=Path(mdp_file),
            gro=Path(gro_file),
            topology=Path(topology_file),
        ),
        gpu_count=_validated_gpu_count(gpu_count),
        gmx_bin=gmx_bin,
        deffnm=deffnm,
        nsteps=nsteps,
        npme=npme,
        maxwarn=maxwarn,
        monitoring_interval_seconds=monitoring_interval_seconds,
        keep_intermediate_files=keep_intermediate_files,
        timeout_seconds=timeout_seconds,
    )
    return _dump(run_doe(settings))


def main(argv: list[str] | None = None) -> None:
    """Run the GROMODEX MCP server.

    Args:
        argv: Optional argument list for tests or programmatic use.
    """
    parser = argparse.ArgumentParser(description="GROMODEX MCP server")
    parser.add_argument(
        "--transport",
        choices=("stdio", "streamable-http", "sse"),
        default=os.getenv("GROMODEX_MCP_TRANSPORT", "stdio"),
    )
    parser.add_argument("--host", default=os.getenv("GROMODEX_MCP_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.getenv("GROMODEX_MCP_PORT", "8000")))
    parser.add_argument("--path", default=os.getenv("GROMODEX_MCP_PATH", "/mcp"))
    args = parser.parse_args(argv)

    mcp.settings.host = args.host
    mcp.settings.port = args.port
    mcp.settings.streamable_http_path = args.path
    if args.transport == "sse":
        mcp.settings.sse_path = args.path
    mcp.run(transport=args.transport)


if __name__ == "__main__":
    main()
