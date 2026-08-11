from __future__ import annotations

import json
from pathlib import Path

from ai_quality.config import ROOT
from ai_quality.evaluation.contracts import EvaluationResult, PerformanceResult, SecurityFinding


def load_normalized(
    directory: str | Path = "reports/normalized",
) -> tuple[list[EvaluationResult], list[SecurityFinding], list[PerformanceResult]]:
    resolved = Path(directory)
    if not resolved.is_absolute():
        resolved = ROOT / resolved
    evaluations: list[EvaluationResult] = []
    findings: list[SecurityFinding] = []
    performance: list[PerformanceResult] = []
    for file in sorted(resolved.glob("*.jsonl")):
        for line in file.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            payload = json.loads(line)
            kind = payload.pop("kind", "evaluation")
            if kind == "security":
                findings.append(SecurityFinding.model_validate(payload))
            elif kind == "performance":
                performance.append(PerformanceResult.model_validate(payload))
            else:
                evaluations.append(EvaluationResult.model_validate(payload))
    return evaluations, findings, performance
