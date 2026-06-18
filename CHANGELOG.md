# Changelog

All notable changes to GROMODEX are documented here.

## [0.1.0] - 2026-06-18

### Added
- Source-layout Python package with typed modules.
- Agent-facing CLI manifest through `gromodex tools` and `AGENTS.md` usage guidance.
- FastMCP server exposing `server_info`, `preview_doe`, `generate_doe`, `collect_doe_results`, and `run_gromacs_doe` tools.
- Pydantic schemas for design rows, run settings, subprocess results, and DOE summaries.
- uv-compatible `pyproject.toml`, local pre-commit checks, MkDocs documentation, and focused tests.

### Changed
- Replaced import-time script execution with explicit CLI commands.
- Replaced `pyDOE3`, `numpy`, and `pandas` usage with standard-library Cartesian product and CSV handling.
- Replaced shell command strings with argument-list subprocess calls.
- Made 4-GPU factor ordering deterministic instead of relying on `set` ordering.
- Made result collection respect custom GROMACS `deffnm` log names.
- Reduced GPU polling overhead by changing the default interval from 0.1 seconds to 1.0 second.

### Removed
- Removed the root-level `gromodex.py` compatibility wrapper after the package CLI became the supported entry point.
- Removed duplicated docs changelog content from the MkDocs site; `CHANGELOG.md` is the single release-history source.

### Security
- Removed `shell=True` command execution from the GROMACS workflow.
- Added validation for supported GPU counts, GPU task strings, positive numeric settings, and path-like `deffnm` values.
