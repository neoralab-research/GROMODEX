"""Agent-facing metadata for CLI discovery."""

from __future__ import annotations

from typing import Any

from gromodex.version import __version__


def agent_manifest() -> dict[str, Any]:
    """Return a JSON-compatible description of the agent-usable CLI surface."""
    return {
        "name": "gromodex",
        "version": __version__,
        "transport": "cli",
        "description": "GROMACS DOE benchmarking through JSON-producing CLI commands.",
        "entrypoint": {
            "source_checkout": ["uv", "run", "gromodex"],
            "installed_package": ["gromodex"],
        },
        "discovery_command": ["uv", "run", "gromodex", "tools"],
        "output": {
            "format": "json",
            "stream": "stdout",
            "errors": "Non-zero process exit or JSON summaries with failed_runs > 0.",
        },
        "safety": {
            "shell_invocation": False,
            "validated_inputs": True,
            "preview_is_read_only": True,
            "generate_writes_csv": True,
            "collect_reads_logs_and_writes_csv": True,
            "run_executes_gromacs": True,
        },
        "recommended_workflow": [
            ["uv", "run", "gromodex", "preview", "--gpu-count", "2", "--limit", "5"],
            ["uv", "run", "gromodex", "generate", "--gpu-count", "2"],
            [
                "uv",
                "run",
                "gromodex",
                "run",
                "--workspace",
                "runs/example",
                "--gpu-count",
                "2",
                "--mdp",
                "input/md.mdp",
                "--gro",
                "input/system.gro",
                "--topology",
                "input/topol.top",
            ],
            [
                "uv",
                "run",
                "gromodex",
                "collect",
                "--workspace",
                "runs/example",
                "--design",
                "runs/example/gmx_fullfact_doe.csv",
            ],
        ],
        "tools": [
            {
                "name": "preview",
                "description": "Return row count, factors, and the first DOE rows without writing files.",
                "command": ["uv", "run", "gromodex", "preview"],
                "side_effects": "none",
                "arguments": [
                    {"name": "--gpu-count", "type": "integer", "choices": [2, 3, 4], "default": 2},
                    {"name": "--limit", "type": "integer", "default": 10},
                ],
            },
            {
                "name": "generate",
                "description": "Write the deterministic DOE CSV and return a summary.",
                "command": ["uv", "run", "gromodex", "generate"],
                "side_effects": "writes the design CSV",
                "arguments": [
                    {"name": "--gpu-count", "type": "integer", "choices": [2, 3, 4], "default": 2},
                    {"name": "--output", "type": "path", "default": "gmx_fullfact_doe.csv"},
                ],
            },
            {
                "name": "collect",
                "description": "Read numbered run directories and write a results CSV.",
                "command": ["uv", "run", "gromodex", "collect"],
                "side_effects": "reads run logs and writes the results CSV",
                "arguments": [
                    {"name": "--workspace", "type": "path", "default": "."},
                    {"name": "--design", "type": "path", "default": "gmx_fullfact_doe.csv"},
                    {"name": "--output", "type": "path", "default": "gmx_fullfact_doe_results.csv"},
                    {"name": "--deffnm", "type": "string", "default": "md"},
                ],
            },
            {
                "name": "run",
                "description": "Prepare a TPR file, execute every DOE row with GROMACS, monitor GPUs, and collect results.",
                "command": ["uv", "run", "gromodex", "run"],
                "side_effects": "executes GROMACS and writes workspace outputs",
                "requires_external_binary": "gmx or --gmx-bin",
                "arguments": [
                    {"name": "--workspace", "type": "path", "default": "."},
                    {"name": "--gpu-count", "type": "integer", "choices": [2, 3, 4], "default": 2},
                    {"name": "--mdp", "type": "path", "required": True},
                    {"name": "--gro", "type": "path", "required": True},
                    {"name": "--topology", "type": "path", "required": True},
                    {"name": "--gmx-bin", "type": "string", "default": "gmx"},
                    {"name": "--deffnm", "type": "string", "default": "md"},
                    {"name": "--nsteps", "type": "integer", "default": 25000},
                    {"name": "--npme", "type": "integer", "default": 1},
                    {"name": "--maxwarn", "type": "integer", "default": 2},
                    {"name": "--monitoring-interval-seconds", "type": "number", "default": 1.0},
                    {"name": "--timeout-seconds", "type": "integer", "default": None},
                    {"name": "--keep-intermediate-files", "type": "boolean", "default": False},
                ],
            },
        ],
    }
