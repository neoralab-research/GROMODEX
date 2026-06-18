from pathlib import Path

import pytest
from pydantic import ValidationError

from gromodex.schemas import DesignPoint, GromacsInputFiles, GromodexRunSettings


def test_design_point_rejects_non_numeric_gputasks() -> None:
    with pytest.raises(ValidationError):
        DesignPoint(ntmpi=2, pin="off", gputasks="gpu0", bonded="cpu", update="gpu")


def test_run_settings_rejects_path_like_deffnm() -> None:
    with pytest.raises(ValidationError):
        GromodexRunSettings(
            input_files=GromacsInputFiles(
                mdp=Path("md.mdp"),
                gro=Path("system.gro"),
                topology=Path("topol.top"),
            ),
            deffnm="nested/md",
        )
