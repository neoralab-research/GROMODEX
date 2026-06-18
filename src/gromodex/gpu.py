"""GPU usage monitoring helpers."""

from __future__ import annotations

import csv
import time
from pathlib import Path
from subprocess import Popen
from typing import Any


def _get_gpus() -> list[Any]:
    """Return GPUtil GPU objects, or an empty list when GPUtil is unavailable."""
    try:
        import GPUtil
    except ImportError:
        return []
    return list(GPUtil.getGPUs())


def monitor_gpu_usage(process: Popen[bytes], path: Path, interval_seconds: float) -> None:
    """Write GPU usage samples while a subprocess is running.

    Args:
        process: Running simulation subprocess.
        path: CSV destination.
        interval_seconds: Delay between samples.
    """
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Time", "GPU ID", "Load (%)", "Memory Used (MB)", "Memory Total (MB)"])
        while process.poll() is None:
            for gpu in _get_gpus():
                writer.writerow(
                    [
                        time.strftime("%H:%M:%S"),
                        gpu.id,
                        gpu.load * 100,
                        gpu.memoryUsed,
                        gpu.memoryTotal,
                    ]
                )
            csv_file.flush()
            time.sleep(interval_seconds)
