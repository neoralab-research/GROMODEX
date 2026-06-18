from pathlib import Path

import pytest

from gromodex.design import generate_design, write_design_csv
from gromodex.results import parse_performance
from gromodex.runner import collect_results_from_csv


def test_parse_performance_reads_gromacs_log(tmp_path: Path) -> None:
    log = tmp_path / "md.log"
    log.write_text("Header\nPerformance:     123.456        ns/day\nFooter\n", encoding="utf-8")
    assert parse_performance(log) == 123.456


def test_parse_performance_missing_line_returns_none(tmp_path: Path) -> None:
    log = tmp_path / "md.log"
    log.write_text("No performance here\n", encoding="utf-8")
    assert parse_performance(log) is None


def test_collect_results_from_csv(tmp_path: Path) -> None:
    design = generate_design(2)[:2]
    design_path = write_design_csv(design, tmp_path / "design.csv")
    run_one = tmp_path / "1"
    run_two = tmp_path / "2"
    run_one.mkdir()
    run_two.mkdir()
    (run_one / "md.log").write_text("Performance: 10.5 ns/day\n", encoding="utf-8")
    (run_two / "md.log").write_text("Performance: 20.0 ns/day\n", encoding="utf-8")

    summary = collect_results_from_csv(tmp_path, design_path, tmp_path / "results.csv")

    assert summary.runs == 2
    assert summary.failed_runs == 0
    assert summary.results[0].performance_ns_per_day == 10.5
    assert (tmp_path / "results.csv").exists()


def test_collect_results_from_csv_supports_custom_deffnm(tmp_path: Path) -> None:
    design = generate_design(2)[:1]
    design_path = write_design_csv(design, tmp_path / "design.csv")
    run_one = tmp_path / "1"
    run_one.mkdir()
    (run_one / "prod.log").write_text("Performance: 42.0 ns/day\n", encoding="utf-8")

    summary = collect_results_from_csv(
        tmp_path, design_path, tmp_path / "results.csv", deffnm="prod"
    )

    assert summary.failed_runs == 0
    assert summary.results[0].performance_ns_per_day == 42.0


def test_collect_results_from_csv_rejects_path_like_deffnm(tmp_path: Path) -> None:
    design = generate_design(2)[:1]
    design_path = write_design_csv(design, tmp_path / "design.csv")

    with pytest.raises(ValueError):
        collect_results_from_csv(tmp_path, design_path, tmp_path / "results.csv", deffnm="../md")
