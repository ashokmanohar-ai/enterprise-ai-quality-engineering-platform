from __future__ import annotations

import importlib.metadata
import os
import shutil
import subprocess
import uuid

from ai_quality.config import Settings, get_settings
from ai_quality.evaluation.contracts import RunMetadata
from ai_quality.evaluation.datasets import dataset_version

TOOLS = [
    "deepeval",
    "ragas",
    "pyrit",
    "garak",
    "mteb",
    "mcp",
    "aiperf",
    "arize-phoenix",
    "langfuse",
    "openai",
]


def _git(*args: str) -> str:
    executable = shutil.which("git")
    if not executable:
        return "unknown"
    completed = subprocess.run(  # noqa: S603
        [executable, *args], check=False, capture_output=True, text=True
    )
    return completed.stdout.strip() or "unknown"


def build_metadata(
    settings: Settings | None = None, dataset: str = "datasets/golden/golden.jsonl"
) -> RunMetadata:
    configured = settings or get_settings()
    versions: dict[str, str] = {}
    for tool in TOOLS:
        try:
            versions[tool] = importlib.metadata.version(tool)
        except importlib.metadata.PackageNotFoundError:
            versions[tool] = "not-installed"
    return RunMetadata(
        evaluation_run_id=os.getenv("AIQ_RUN_ID", str(uuid.uuid4())),
        experiment_id=os.getenv("AIQ_EXPERIMENT_ID"),
        git_commit=os.getenv("GITHUB_SHA", _git("rev-parse", "HEAD")),
        branch=os.getenv("GITHUB_REF_NAME", _git("branch", "--show-current")),
        dataset_version=dataset_version(dataset),
        prompt_version=os.getenv("AIQ_PROMPT_VERSION", "customer-support-v2"),
        model_deployment=configured.azure_openai_chat_deployment,
        evaluator_deployment=configured.azure_openai_evaluator_deployment,
        embedding_deployment=configured.azure_openai_embedding_deployment,
        retriever_settings={"top_k": 3, "store": "in_memory_reference"},
        tool_versions=versions,
        random_seed=configured.aiq_random_seed,
        environment=os.getenv("AIQ_ENVIRONMENT", "local"),
    )
