"""GROMACS result parsing and result CSV writing."""

from __future__ import annotations

import csv
import re
from pathlib import Path

from gromodex.factors import FACTOR_FIELDS
from gromodex.schemas import DesignPoint, DesignRunResult, DoeRunSummary, validate_deffnm_stem

_PERFORMANCE_RE = re.compile(r"^\s*Performance:\s+([0-9]+(?:\.[0-9]+)?)", re.MULTILINE)


def parse_performance(log_path: Path) -> float | None:
    """Extract ``ns/day`` performance from a GROMACS log file.

    Args:
        log_path: Path to a GROMACS log file.

    Returns:
        Parsed performance value, or ``None`` when no performance line exists.
    """
    if not log_path.exists():
        return None
    match = _PERFORMANCE_RE.search(log_path.read_text(encoding="utf-8", errors="replace"))
    if match is None:
        return None
    return float(match.group(1))


def write_results_csv(results: list[DesignRunResult], path: Path) -> Path:
    """Write DOE results to a CSV file.

    Args:
        results: Collected per-run results.
        path: Destination CSV path.

    Returns:
        The destination path.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=[*FACTOR_FIELDS, "Performance (ns/day)"])
        writer.writeheader()
        for result in results:
            row = result.design.model_dump()
            row["Performance (ns/day)"] = result.performance_ns_per_day or 0
            writer.writerow(row)
    return path


def collect_results(
    workspace: Path,
    design: list[DesignPoint],
    design_path: Path,
    output_path: Path,
    deffnm: str = "md",
) -> DoeRunSummary:
    """Collect performance metrics from numbered run directories.

    Args:
        workspace: Directory containing numbered run folders.
        design: DOE rows corresponding to the numbered folders.
        design_path: Path to the design CSV used for provenance.
        output_path: Destination CSV path.
        deffnm: GROMACS ``-deffnm`` file stem used for run logs.

    Returns:
        Summary containing one result per design point.
    """
    log_name = f"{validate_deffnm_stem(deffnm)}.log"
    results: list[DesignRunResult] = []
    for index, design_point in enumerate(design, start=1):
        run_dir = workspace / str(index)
        performance = parse_performance(run_dir / log_name)
        results.append(
            DesignRunResult(
                run_id=index,
                design=design_point,
                directory=run_dir,
                command=[],
                returncode=0 if performance is not None else 1,
                performance_ns_per_day=performance,
                error=None if performance is not None else f"Performance not found in {log_name}",
            )
        )
    results_path = write_results_csv(results, output_path)
    return DoeRunSummary(
        workspace=workspace,
        design_path=design_path,
        results_path=results_path,
        runs=len(results),
        failed_runs=sum(1 for result in results if result.error),
        results=results,
    )
