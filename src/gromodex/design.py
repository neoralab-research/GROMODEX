"""Full-factorial design generation and CSV I/O."""

from __future__ import annotations

import csv
from itertools import product
from pathlib import Path

from gromodex.factors import FACTOR_FIELDS, FactorLevels, factor_levels_for_gpu
from gromodex.schemas import DesignPoint, DesignSummary, GPUCount


def factors_for_gpu(gpu_count: GPUCount) -> FactorLevels:
    """Return factorial levels for a supported GPU count.

    Args:
        gpu_count: Number of GPUs to target.

    Returns:
        Mapping from factor name to ordered levels.
    """
    return factor_levels_for_gpu(gpu_count)


def generate_design(gpu_count: GPUCount = 2) -> list[DesignPoint]:
    """Generate a deterministic full-factorial DOE.

    Args:
        gpu_count: Number of GPUs to target.

    Returns:
        Ordered design points.
    """
    factors = factors_for_gpu(gpu_count)

    rows: list[DesignPoint] = []
    for ntmpi, pin, gputasks, bonded, update in product(
        factors["ntmpi"],
        factors["pin"],
        factors["gputasks"],
        factors["bonded"],
        factors["update"],
    ):
        rows.append(
            DesignPoint(
                ntmpi=ntmpi,
                pin=pin,
                gputasks=gputasks,
                bonded=bonded,
                update=update,
            )
        )
    return rows


def summarize_design(gpu_count: GPUCount = 2, preview_limit: int = 10) -> DesignSummary:
    """Build a compact summary of the generated DOE.

    Args:
        gpu_count: Number of GPUs to target.
        preview_limit: Maximum preview rows to include.

    Returns:
        Design metadata and the first preview rows.
    """
    design = generate_design(gpu_count)
    return DesignSummary(
        gpu_count=gpu_count,
        rows=len(design),
        factors=list(FACTOR_FIELDS),
        preview=design[: max(preview_limit, 0)],
    )


def write_design_csv(design: list[DesignPoint], path: Path) -> Path:
    """Write design points to a CSV file.

    Args:
        design: Design rows to serialize.
        path: Destination path.

    Returns:
        The destination path.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=FACTOR_FIELDS)
        writer.writeheader()
        for row in design:
            writer.writerow(row.model_dump())
    return path


def read_design_csv(path: Path) -> list[DesignPoint]:
    """Read design points from a CSV file.

    Args:
        path: CSV path written by :func:`write_design_csv`.

    Returns:
        Parsed design points.
    """
    with path.open(newline="", encoding="utf-8") as csv_file:
        return [DesignPoint.model_validate(row) for row in csv.DictReader(csv_file)]
