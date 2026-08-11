from __future__ import annotations

import subprocess
from pathlib import Path

from ai_quality.config import ROOT, Settings, get_settings, load_yaml


def run(profile: str = "smoke", settings: Settings | None = None) -> Path:
    configured = settings or get_settings()
    if not configured.aiq_security_authorized:
        raise PermissionError(
            "Garak scanning requires AIQ_SECURITY_AUTHORIZED=true and target-owner authorization."
        )
    security = load_yaml("config/security.yaml")
    spec = security["profiles"][profile]["garak_spec"]
    configured.require_azure()
    assert configured.azure_openai_endpoint and configured.azure_openai_chat_deployment
    target = (
        f"{configured.azure_openai_endpoint}/openai/deployments/"
        f"{configured.azure_openai_chat_deployment}/chat/completions"
        f"?api-version={configured.azure_openai_api_version}"
    )
    prefix = ROOT / "reports" / "security" / f"garak-{profile}"
    prefix.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "python",
        "-m",
        "garak",
        "--config",
        "garak/configs/azure-rest.yaml",
        "--target-name",
        target,
        "--spec",
        spec,
        "--report_prefix",
        str(prefix),
    ]
    completed = subprocess.run(command, cwd=ROOT, check=False)  # noqa: S603
    if completed.returncode:
        raise RuntimeError(
            f"Garak returned {completed.returncode}; inspect the private retained report."
        )
    candidates = sorted(prefix.parent.glob(f"{prefix.name}*.report.jsonl"))
    if not candidates:
        candidates = sorted(prefix.parent.glob(f"{prefix.name}*.jsonl"))
    if not candidates:
        raise RuntimeError("Garak completed without the expected JSONL report.")
    return candidates[-1]
