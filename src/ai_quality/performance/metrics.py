from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ai_quality.evaluation.contracts import PerformanceResult

METRIC_ALIASES = {
    "request_latency": "p95_latency_ms",
    "time_to_first_token": "p95_ttft_ms",
    "inter_token_latency": "p95_itl_ms",
    "request_throughput": "requests_per_second",
    "output_token_throughput": "output_tokens_per_second",
    "error_rate": "error_rate",
}


def normalize_aiperf(
    path: str | Path, scenario: str, thresholds: dict[str, Any]
) -> list[PerformanceResult]:
    """Normalize AIPerf JSON exports without renaming unsupported native metrics."""
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    statistics = payload.get("statistics", payload.get("metrics", payload))
    results: list[PerformanceResult] = []
    for native, internal in METRIC_ALIASES.items():
        block = statistics.get(native)
        if native == "error_rate" and block is None:
            succeeded = statistics.get("request_count", {})
            failed = statistics.get("error_request_count", {})
            succeeded_value = (
                succeeded.get("avg", succeeded.get("value", 0))
                if isinstance(succeeded, dict)
                else succeeded
            )
            failed_value = (
                failed.get("avg", failed.get("value", 0)) if isinstance(failed, dict) else failed
            )
            total = float(succeeded_value or 0) + float(failed_value or 0)
            block = {"value": float(failed_value or 0) / total if total else 0.0, "unit": "ratio"}
        if block is None:
            continue
        if isinstance(block, dict):
            value = (
                block.get("p95")
                if internal.startswith("p95_")
                else block.get("avg", block.get("value"))
            )
            unit = str(
                block.get(
                    "unit",
                    "ms"
                    if "latency" in internal or "ttft" in internal or "itl" in internal
                    else "count/s",
                )
            )
        else:
            value, unit = block, "ratio" if internal == "error_rate" else "count/s"
        if value is None:
            continue
        rule = thresholds.get(internal, {})
        comparison = "max" if "max" in rule else "min" if "min" in rule else None
        threshold = rule.get(comparison) if comparison else None
        passed = (
            True
            if threshold is None
            else float(value) <= float(threshold)
            if comparison == "max"
            else float(value) >= float(threshold)
        )
        results.append(
            PerformanceResult(
                scenario=scenario,
                metric=internal,
                value=float(value),
                unit=unit,
                threshold=threshold,
                comparison=comparison,
                passed=passed,
                metadata={"native_metric": native},
            )
        )
    return results
