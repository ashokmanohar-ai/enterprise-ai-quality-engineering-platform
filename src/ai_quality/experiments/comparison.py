from __future__ import annotations

from typing import Any


def compare_baseline(
    baseline: dict[str, float],
    candidate: dict[str, float],
    *,
    max_quality_drop: float,
    critical_metrics: set[str] | None = None,
) -> list[dict[str, Any]]:
    critical = critical_metrics or set()
    comparisons: list[dict[str, Any]] = []
    for metric in sorted(set(baseline) | set(candidate)):
        before = baseline.get(metric)
        after = candidate.get(metric)
        if before is None or after is None:
            classification = "neutral"
            delta = None
        else:
            delta = after - before
            if delta > max_quality_drop:
                classification = "improvement"
            elif delta >= -max_quality_drop:
                classification = "neutral"
            elif metric in critical:
                classification = "blocking_regression"
            else:
                classification = "non_blocking_regression"
        comparisons.append(
            {
                "metric": metric,
                "baseline": before,
                "candidate": after,
                "delta": delta,
                "classification": classification,
            }
        )
    return comparisons
