"""Execution workflow for GROMACS DOE runs."""

from __future__ import annotations

import logging
import shutil
import subprocess
from pathlib import Path

from gromodex.design import generate_design, read_design_csv, write_design_csv
from gromodex.errors import GromodexError
from gromodex.gpu import monitor_gpu_usage
from gromodex.results import collect_results, parse_performance, write_results_csv
from gromodex.schemas import (
    CommandResult,
    DesignPoint,
    DesignRunResult,
    DoeRunSummary,
    GromodexRunSettings,
)

LOGGER = logging.getLogger(__name__)


def resolve_input_path(path: Path) -> Path:
    """Resolve a required input path and fail with a clear error if missing.

    Args:
        path: File path to resolve.

    Returns:
        Absolute path to the existing file.

    Raises:
        GromodexError: If the file does not exist.
    """
    resolved = path.expanduser().resolve()
    if not resolved.is_file():
        msg = f"Input file does not exist: {path}"
        raise GromodexError(msg)
    return resolved


def run_command(command: list[str], cwd: Path, timeout_seconds: int | None = None) -> CommandResult:
    """Run a command without invoking a shell.

    Args:
        command: Command and arguments.
        cwd: Working directory.
        timeout_seconds: Optional subprocess timeout.

    Returns:
        Captured command result.
    """
    completed = subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        check=False,
        text=True,
        timeout=timeout_seconds,
    )
    return CommandResult(
        command=command,
        cwd=cwd,
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )


def build_grompp_command(settings: GromodexRunSettings, tpr_path: Path) -> list[str]:
    """Build the ``gmx grompp`` command for a DOE workspace.

    Args:
        settings: Validated run settings.
        tpr_path: Destination TPR path.

    Returns:
        Command argument list.
    """
    inputs = settings.input_files
    return [
        settings.gmx_bin,
        "grompp",
        "-f",
        str(resolve_input_path(inputs.mdp)),
        "-o",
        str(tpr_path),
        "-c",
        str(resolve_input_path(inputs.gro)),
        "-p",
        str(resolve_input_path(inputs.topology)),
        "-v",
        "-maxwarn",
        str(settings.maxwarn),
    ]


def build_mdrun_command(settings: GromodexRunSettings, design_point: DesignPoint) -> list[str]:
    """Build a ``gmx mdrun`` command for one design point.

    Args:
        settings: Validated run settings.
        design_point: DOE point to execute.

    Returns:
        Command argument list.
    """
    return [
        settings.gmx_bin,
        "mdrun",
        "-v",
        "-notunepme",
        "-resethway",
        "-deffnm",
        settings.deffnm,
        "-nb",
        "gpu",
        "-nsteps",
        str(settings.nsteps),
        "-npme",
        str(settings.npme),
        "-ntmpi",
        str(design_point.ntmpi),
        "-pin",
        design_point.pin,
        "-gputasks",
        design_point.gputasks,
        "-pme",
        "gpu",
        "-pmefft",
        "gpu",
        "-bonded",
        design_point.bonded,
        "-update",
        design_point.update,
    ]


def clean_run_directory(run_dir: Path, keep_files: set[str]) -> None:
    """Remove temporary files from a run directory.

    Args:
        run_dir: Directory to clean.
        keep_files: File names that must remain.
    """
    for path in run_dir.iterdir():
        if path.name in keep_files:
            continue
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink(missing_ok=True)


def execute_design_point(
    settings: GromodexRunSettings,
    design_point: DesignPoint,
    run_id: int,
    tpr_path: Path,
) -> DesignRunResult:
    """Execute one design point and collect its performance.

    Args:
        settings: Validated run settings.
        design_point: DOE point to execute.
        run_id: One-based run identifier.
        tpr_path: Prepared GROMACS TPR file.

    Returns:
        Per-run result model.
    """
    workspace = settings.workspace.expanduser().resolve()
    run_dir = workspace / str(run_id)
    if run_dir.exists():
        msg = f"Run directory already exists: {run_dir}"
        raise GromodexError(msg)

    run_dir.mkdir(parents=True)
    shutil.copy2(tpr_path, run_dir / f"{settings.deffnm}.tpr")
    command = build_mdrun_command(settings, design_point)
    gpu_usage_path = run_dir / f"gpu_usage_run{run_id}.csv"
    error: str | None = None

    try:
        process = subprocess.Popen(command, cwd=run_dir)
        monitor_gpu_usage(process, gpu_usage_path, settings.monitoring_interval_seconds)
        returncode = process.wait(timeout=settings.timeout_seconds)
    except Exception as exc:
        returncode = 1
        error = f"{type(exc).__name__}: {exc}"
        LOGGER.exception("Cannot execute run %s", run_id)

    performance = parse_performance(run_dir / f"{settings.deffnm}.log")
    if performance is None and error is None:
        error = f"Performance not found in {settings.deffnm}.log"

    if not settings.keep_intermediate_files:
        clean_run_directory(run_dir, {f"{settings.deffnm}.log", gpu_usage_path.name})

    return DesignRunResult(
        run_id=run_id,
        design=design_point,
        directory=run_dir,
        command=command,
        returncode=returncode,
        performance_ns_per_day=performance,
        error=error,
    )


def run_doe(settings: GromodexRunSettings) -> DoeRunSummary:
    """Generate and execute a complete GROMACS DOE.

    Args:
        settings: Validated run settings.

    Returns:
        Summary of generated design and executed runs.

    Raises:
        GromodexError: If preparing the GROMACS input fails.
    """
    workspace = settings.workspace.expanduser().resolve()
    workspace.mkdir(parents=True, exist_ok=True)

    design = generate_design(settings.gpu_count)
    design_path = write_design_csv(design, workspace / "gmx_fullfact_doe.csv")
    tpr_path = workspace / f"{settings.deffnm}.tpr"

    logging.basicConfig(
        filename=workspace / "doe.log",
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        force=True,
    )
    LOGGER.info("Generated %s DOE rows at %s", len(design), design_path)

    grompp_result = run_command(
        build_grompp_command(settings, tpr_path),
        cwd=workspace,
        timeout_seconds=settings.timeout_seconds,
    )
    if grompp_result.returncode != 0:
        msg = f"gmx grompp failed with exit code {grompp_result.returncode}: {grompp_result.stderr}"
        raise GromodexError(msg)

    results = [
        execute_design_point(settings, design_point, run_id, tpr_path)
        for run_id, design_point in enumerate(design, start=1)
    ]
    results_path = write_results_csv(results, workspace / "gmx_fullfact_doe_results.csv")
    return DoeRunSummary(
        workspace=workspace,
        design_path=design_path,
        results_path=results_path,
        runs=len(results),
        failed_runs=sum(1 for result in results if result.error or result.returncode != 0),
        results=results,
    )


def collect_results_from_csv(
    workspace: Path, design_path: Path, output_path: Path, deffnm: str = "md"
) -> DoeRunSummary:
    """Collect results for a previously generated DOE CSV.

    Args:
        workspace: Directory containing numbered run folders.
        design_path: Path to the design CSV.
        output_path: Destination results CSV.
        deffnm: GROMACS ``-deffnm`` file stem used for run logs.

    Returns:
        Collection summary.
    """
    resolved_workspace = workspace.expanduser().resolve()
    resolved_design_path = design_path.expanduser().resolve()
    design = read_design_csv(resolved_design_path)
    return collect_results(
        resolved_workspace,
        design,
        resolved_design_path,
        output_path.expanduser().resolve(),
        deffnm=deffnm,
    )
