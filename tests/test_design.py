from pathlib import Path

from gromodex.design import generate_design, read_design_csv, summarize_design, write_design_csv


def test_generate_design_counts_are_stable() -> None:
    assert len(generate_design(2)) == 600
    assert len(generate_design(3)) == 280
    assert len(generate_design(4)) == 1408


def test_generate_design_is_deterministic() -> None:
    first = generate_design(4)[:5]
    second = generate_design(4)[:5]
    assert first == second
    assert first[0].model_dump() == {
        "ntmpi": 2,
        "pin": "off",
        "gputasks": "01",
        "bonded": "cpu",
        "update": "cpu",
    }


def test_write_and_read_design_csv(tmp_path: Path) -> None:
    design = generate_design(2)[:3]
    path = write_design_csv(design, tmp_path / "design.csv")
    assert read_design_csv(path) == design


def test_summarize_design_preview_limit() -> None:
    summary = summarize_design(2, preview_limit=2)
    assert summary.rows == 600
    assert len(summary.preview) == 2
