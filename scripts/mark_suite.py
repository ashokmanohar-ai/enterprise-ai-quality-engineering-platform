from __future__ import annotations

import sys
from pathlib import Path

from ai_quality.evaluation.contracts import EvaluationResult


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: python scripts/mark_suite.py <suite>")
    suite = sys.argv[1]
    result = EvaluationResult(
        test_id=f"suite:{suite}",
        framework="aiq",
        category="suite",
        metric="suite_completed",
        score=1.0,
        threshold=1.0,
        passed=True,
        metadata={"suite": suite},
    )
    path = Path("reports/normalized") / f"suite-{suite}.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(result.model_dump_json() + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
