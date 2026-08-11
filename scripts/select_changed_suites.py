from __future__ import annotations

import shutil
import subprocess
import sys

ALL_PR = {"llm", "rag", "prompt_regression", "agent", "mcp", "security_smoke"}

ROUTES = {
    "prompts/": {"llm", "prompt_regression"},
    "promptfoo/": {"prompt_regression", "security_smoke"},
    "src/ai_quality/applications/llm": {"llm", "prompt_regression"},
    "src/ai_quality/applications/rag": {"rag"},
    "src/ai_quality/retrieval/": {"rag"},
    "knowledge_base/": {"rag"},
    "src/ai_quality/models/embeddings": {"embeddings", "rag"},
    "mteb/": {"embeddings"},
    "src/ai_quality/applications/agent": {"agent", "mcp", "security_smoke"},
    "src/ai_quality/mcp/": {"mcp", "agent"},
    "mcp/": {"mcp", "agent"},
    "config/security": {"security_smoke"},
    "src/ai_quality/security/": {"security_smoke"},
    "src/ai_quality/evaluation/contracts": ALL_PR,
    "src/ai_quality/evaluation/datasets": ALL_PR,
    "config/quality-gates": ALL_PR,
    "pyproject.toml": ALL_PR,
    "package.json": {"prompt_regression", "security_smoke", "mcp"},
    "config/models": {"llm", "rag", "performance"},
    "src/ai_quality/models/azure": {"llm", "rag", "performance"},
}


def main(base: str) -> None:
    executable = shutil.which("git")
    if not executable:
        raise RuntimeError("git is required for changed-file selection")
    completed = subprocess.run(  # noqa: S603
        [executable, "diff", "--name-only", f"{base}...HEAD"],
        check=True,
        capture_output=True,
        text=True,
    )
    files = completed.stdout.splitlines()
    suites = {"deterministic"}
    for file in files:
        for prefix, routed in ROUTES.items():
            if file.startswith(prefix):
                suites.update(routed)
    print(",".join(sorted(suites)))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "origin/main")
