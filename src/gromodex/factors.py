"""DOE factor definitions and level selection."""

from __future__ import annotations

from typing import Final, TypedDict, TypeVar

from gromodex.schemas import ComputeTarget, GPUCount, PinMode

FACTOR_FIELDS: Final[tuple[str, ...]] = ("ntmpi", "pin", "gputasks", "bonded", "update")
PIN_LEVELS: Final[list[PinMode]] = ["off", "on"]
COMPUTE_TARGET_LEVELS: Final[list[ComputeTarget]] = ["cpu", "gpu"]

_NTMPI_BY_GPU: Final[dict[GPUCount, list[int]]] = {
    2: [2, 4, 6, 8, 10],
    3: [3, 6, 9, 12, 15],
    4: [4, 8, 12, 16, 20],
}
_GPUTASKS_BY_GPU: Final[dict[GPUCount, list[str]]] = {
    2: [
        "01",
        "0011",
        "0001",
        "000111",
        "000011",
        "000001",
        "00001111",
        "00000111",
        "00000011",
        "00000001",
        "0000011111",
        "0000001111",
        "0000000111",
        "0000000011",
        "0000000001",
    ],
    3: [
        "012",
        "001122",
        "000112",
        "000111222",
        "000011112",
        "000011112222",
        "000000111112",
    ],
    4: [
        "0123",
        "00112233",
        "00011223",
        "000111222333",
        "000011112223",
        "0000111122223333",
        "0000011111222223",
    ],
}

_T = TypeVar("_T", int, str)


class FactorLevels(TypedDict):
    """Ordered levels for every DOE factor."""

    ntmpi: list[int]
    pin: list[PinMode]
    gputasks: list[str]
    bonded: list[ComputeTarget]
    update: list[ComputeTarget]


def _unique_preserving_order(values: list[_T]) -> list[_T]:
    """Return unique values without the non-determinism of ``set`` ordering."""
    seen: set[_T] = set()
    unique: list[_T] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        unique.append(value)
    return unique


def factor_levels_for_gpu(gpu_count: GPUCount) -> FactorLevels:
    """Return ordered factorial levels for a supported GPU count."""
    if gpu_count == 4:
        ntmpi = _unique_preserving_order(_NTMPI_BY_GPU[2] + _NTMPI_BY_GPU[4])
        gputasks = _unique_preserving_order(_GPUTASKS_BY_GPU[2] + _GPUTASKS_BY_GPU[4])
    else:
        ntmpi = _NTMPI_BY_GPU[gpu_count].copy()
        gputasks = _GPUTASKS_BY_GPU[gpu_count].copy()

    return {
        "ntmpi": ntmpi,
        "pin": PIN_LEVELS.copy(),
        "gputasks": gputasks,
        "bonded": COMPUTE_TARGET_LEVELS.copy(),
        "update": COMPUTE_TARGET_LEVELS.copy(),
    }
