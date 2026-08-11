from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from ai_quality.config import ROOT, Settings, get_settings


def run(config: str = "promptfoo/redteam.yaml", settings: Settings | None = None) -> Path:
    configured = settings or get_settings()
    if not configured.aiq_security_authorized:
        raise PermissionError(
            "Security testing requires AIQ_SECURITY_AUTHORIZED=true and target-owner authorization."
        )
    output = ROOT / "reports" / "security" / "promptfoo-redteam.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    executable = shutil.which("npx")
    if not executable:
        raise RuntimeError("npx is required for Promptfoo red-team execution")
    completed = subprocess.run(  # noqa: S603
        [
            executable,
            "promptfoo",
            "redteam",
            "run",
            "-c",
            config,
            "--output",
            str(output),
            "--no-table",
        ],
        cwd=ROOT,
        check=False,
    )
    if completed.returncode:
        raise RuntimeError(f"Promptfoo red-team returned {completed.returncode}")
    return output
