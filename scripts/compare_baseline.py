from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from statistics import mean

from ai_quality.evaluation.contracts import EvaluationResult
from ai_quality.experiments.comparison import compare_baseline
from ai_quality.reporting.aggregate import load_normalized


def main() -> None:
    baseline = json.loads(Path("experiments/baseline/production.json").read_text(encoding="utf-8"))
    results, _, _ = load_normalized()
    grouped: dict[str, list[float]] = defaultdict(list)
    for result in results:
        if result.score is not None and result.metric not in {"suite_completed", "required_suite"}:
            grouped[result.metric].append(result.score)
    candidate = {metric: mean(scores) for metric, scores in grouped.items()}
    comparison = compare_baseline(
        baseline,
        candidate,
        max_quality_drop=0.02,
        critical_metrics={"faithfulness", "context_recall", "agent_task_completion"},
    )
    path = Path("reports/normalized/baseline.jsonl")
    lines: list[str] = []
    for item in comparison:
        blocking = item["classification"] == "blocking_regression"
        lines.append(
            EvaluationResult(
                test_id=f"baseline:{item['metric']}",
                framework="aiq",
                category="regression",
                metric=f"baseline_{item['metric']}",
                score=None,
                passed=not blocking,
                blocking=blocking,
                reason=json.dumps(item),
                metadata={"comparison": item},
            ).model_dump_json()
        )
    lines.append(
        EvaluationResult(
            test_id="suite:baseline",
            framework="aiq",
            category="suite",
            metric="suite_completed",
            score=1.0,
            threshold=1.0,
            passed=True,
            metadata={"suite": "baseline"},
        ).model_dump_json()
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
