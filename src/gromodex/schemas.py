"""Pydantic schemas used by the CLI, services, and MCP tools."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

GPUCount = Literal[2, 3, 4]
PinMode = Literal["off", "on"]
ComputeTarget = Literal["cpu", "gpu"]


def validate_deffnm_stem(value: str) -> str:
    """Reject path-like ``deffnm`` values so runs stay inside their directory."""
    if not value:
        msg = "deffnm must not be empty"
        raise ValueError(msg)
    if "/" in value or "\\" in value:
        msg = "deffnm must be a file stem, not a path"
        raise ValueError(msg)
    return value


class GromodexModel(BaseModel):
    """Base schema with strict fields for predictable agent I/O."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class DesignPoint(GromodexModel):
    """One GROMACS runtime configuration in the factorial design."""

    ntmpi: int = Field(..., gt=0, description="MPI ranks per simulation run.")
    pin: PinMode = Field(..., description="CPU pinning mode passed to gmx mdrun.")
    gputasks: str = Field(..., min_length=1, description="GROMACS GPU task mapping.")
    bonded: ComputeTarget = Field(..., description="Device used for bonded interactions.")
    update: ComputeTarget = Field(..., description="Device used for particle updates.")

    @field_validator("gputasks")
    @classmethod
    def validate_gputasks(cls, value: str) -> str:
        """Validate that GROMACS GPU task mappings contain only GPU indices."""
        if not value.isdigit():
            msg = "gputasks must contain only numeric GPU identifiers"
            raise ValueError(msg)
        return value


class DoeGenerationRequest(GromodexModel):
    """Request for generating a deterministic full-factorial DOE."""

    gpu_count: GPUCount = Field(2, description="Number of GPUs to target.")
    output_path: Path | None = Field(
        default=None,
        description="Optional CSV destination for the generated design.",
    )


class DesignSummary(GromodexModel):
    """Compact summary returned by CLI and MCP design operations."""

    gpu_count: GPUCount
    rows: int
    factors: list[str]
    output_path: Path | None = None
    preview: list[DesignPoint] = Field(default_factory=list)


class GromacsInputFiles(GromodexModel):
    """Input files required to build a GROMACS portable run input."""

    mdp: Path = Field(..., description="Path to the MDP parameter file.")
    gro: Path = Field(..., description="Path to the coordinate file.")
    topology: Path = Field(..., description="Path to the topology file.")


class GromodexRunSettings(GromodexModel):
    """Validated settings for executing a GROMACS DOE run."""

    workspace: Path = Field(Path(), description="Directory where outputs are written.")
    input_files: GromacsInputFiles
    gpu_count: GPUCount = 2
    gmx_bin: str = Field("gmx", min_length=1, description="GROMACS executable.")
    deffnm: str = Field("md", min_length=1, description="GROMACS -deffnm value.")
    nsteps: int = Field(25_000, ge=1, description="Number of MD steps per design point.")
    npme: int = Field(1, ge=0, description="Number of PME ranks.")
    maxwarn: int = Field(2, ge=0, description="gmx grompp -maxwarn value.")
    monitoring_interval_seconds: float = Field(
        1.0,
        gt=0,
        description="GPU usage polling interval.",
    )
    keep_intermediate_files: bool = Field(
        False,
        description="Keep files other than the deffnm log and GPU usage CSV in run directories.",
    )
    timeout_seconds: int | None = Field(
        None,
        gt=0,
        description="Optional timeout for each subprocess call.",
    )

    @field_validator("deffnm")
    @classmethod
    def validate_deffnm(cls, value: str) -> str:
        """Validate that ``deffnm`` is a file stem."""
        return validate_deffnm_stem(value)


class CommandResult(GromodexModel):
    """Captured subprocess result."""

    command: list[str]
    cwd: Path
    returncode: int
    stdout: str = ""
    stderr: str = ""


class DesignRunResult(GromodexModel):
    """Result for one executed design point."""

    run_id: int
    design: DesignPoint
    directory: Path
    command: list[str]
    returncode: int
    performance_ns_per_day: float | None = None
    error: str | None = None


class DoeRunSummary(GromodexModel):
    """Summary returned after running or collecting a DOE."""

    workspace: Path
    design_path: Path
    results_path: Path | None = None
    runs: int
    failed_runs: int = 0
    results: list[DesignRunResult] = Field(default_factory=list)
