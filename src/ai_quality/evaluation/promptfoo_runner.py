from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from ai_quality.config import ROOT
from ai_quality.evaluation.contracts import EvaluationResult


def run_promptfoo(
    config: str, *, output: str = "reports/raw/promptfoo.json"
) -> list[EvaluationResult]:
    output_path = ROOT / output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    command = ["npx", "promptfoo", "eval", "-c", config, "--no-cache", "--output", str(output_path)]
    completed = subprocess.run(command, cwd=ROOT, check=False, capture_output=True, text=True)  # noqa: S603
    if completed.returncode not in {0, 1}:
        raise RuntimeError(
            f"Promptfoo failed without exposing credentials: {completed.stderr[-1000:]}"
        )
    return normalize_promptfoo(output_path)


def normalize_promptfoo(path: str | Path) -> list[EvaluationResult]:
    payload: dict[str, Any] = json.loads(Path(path).read_text(encoding="utf-8"))
    table = payload.get("results", {}).get("results", payload.get("results", []))
    normalized: list[EvaluationResult] = []
    for index, item in enumerate(table):
        test = item.get("testCase", {})
        description = test.get("description") or f"promptfoo-{index:04d}"
        score = item.get("score")
        normalized.append(
            EvaluationResult(
                test_id=description,
                framework="promptfoo",
                category="prompt_regression",
                metric="assertions",
                score=float(score) if isinstance(score, int | float) and 0 <= score <= 1 else None,
                passed=bool(item.get("success", item.get("pass", False))),
                blocking=not bool(item.get("success", item.get("pass", False))),
                reason=str(item.get("gradingResult", {}).get("reason", item.get("error", ""))),
                latency_ms=item.get("latencyMs"),
                metadata={
                    "provider": item.get("provider"),
                    "prompt": item.get("prompt", {}).get("label"),
                },
            )
        )
    return normalized
