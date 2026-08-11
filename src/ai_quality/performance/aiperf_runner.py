from __future__ import annotations

import subprocess

from ai_quality.config import ROOT, Settings, get_settings, load_yaml


def run(scenario: str = "smoke", settings: Settings | None = None):  # type: ignore[no-untyped-def]
    configured = settings or get_settings()
    if not configured.aiq_performance_authorized:
        raise PermissionError(
            "Load testing requires AIQ_PERFORMANCE_AUTHORIZED=true and target-owner authorization."
        )
    configured.require_azure()
    spec = load_yaml("config/performance.yaml")["scenarios"][scenario]
    assert configured.azure_openai_api_key
    assert configured.azure_openai_endpoint and configured.azure_openai_chat_deployment
    output = ROOT / "reports" / "raw" / "aiperf" / scenario
    output.mkdir(parents=True, exist_ok=True)
    command = [
        "aiperf",
        "profile",
        "--model",
        configured.azure_openai_chat_deployment,
        "--endpoint-type",
        "chat",
        "--endpoint",
        f"/openai/deployments/{{model}}/chat/completions?api-version={configured.azure_openai_api_version}",
        "--url",
        configured.azure_openai_endpoint,
        "--header",
        f"api-key:{configured.azure_openai_api_key.get_secret_value()}",
        "--input-file",
        "datasets/performance/prompts.jsonl",
        "--custom-dataset-type",
        "single_turn",
        "--streaming",
        "--concurrency",
        str(spec["concurrency"]),
        "--output-artifact-dir",
        str(output),
        "--export-level",
        "summary",
        "--ui-type",
        "none",
    ]
    if spec.get("duration_seconds"):
        command.extend(["--benchmark-duration", str(spec["duration_seconds"])])
    else:
        command.extend(["--request-count", str(spec["request_count"])])
    if spec.get("warmup_requests"):
        command.extend(["--warmup-request-count", str(spec["warmup_requests"])])
    completed = subprocess.run(command, cwd=ROOT, check=False)  # noqa: S603
    if completed.returncode:
        raise RuntimeError(f"AIPerf returned {completed.returncode}")
    return output / "profile_export_aiperf.json"
