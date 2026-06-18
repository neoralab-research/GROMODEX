from pathlib import Path

import pytest

from gromodex.errors import GromodexError
from gromodex.runner import build_mdrun_command, resolve_input_path
from gromodex.schemas import DesignPoint, GromacsInputFiles, GromodexRunSettings


def test_build_mdrun_command_uses_argument_list() -> None:
    settings = GromodexRunSettings(
        input_files=GromacsInputFiles(
            mdp=Path("md.mdp"),
            gro=Path("system.gro"),
            topology=Path("topol.top"),
        ),
        nsteps=100,
    )
    design = DesignPoint(ntmpi=2, pin="on", gputasks="01", bonded="gpu", update="cpu")

    command = build_mdrun_command(settings, design)

    assert command[:2] == ["gmx", "mdrun"]
    assert "-ntmpi" in command
    assert "2" in command
    assert all(" " not in item for item in command)


def test_resolve_input_path_requires_existing_file(tmp_path: Path) -> None:
    with pytest.raises(GromodexError):
        resolve_input_path(tmp_path / "missing.mdp")
