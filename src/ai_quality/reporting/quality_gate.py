from __future__ import annotations

from collections import defaultdict
from statistics import mean
from typing import Any

from ai_quality.evaluation.contracts import (
    EvaluationResult,
    PerformanceResult,
    QualityReport,
    RunMetadata,
    SecurityFinding,
    Severity,
)


def _profile(config: dict[str, Any], profile: str) -> dict[str, Any]:
    selected = dict(config["profiles"][profile])
    if "extends" in selected:
        parent = dict(config["profiles"][selected.pop("extends")])
        for key, value in selected.items():
            if isinstance(value, dict) and isinstance(parent.get(key), dict):
                parent[key] = {**parent[key], **value}
            else:
                parent[key] = value
        selected = parent
    return selected


def evaluate_gate(
    *,
    profile: str,
    gate_config: dict[str, Any],
    results: list[EvaluationResult],
    security_findings: list[SecurityFinding],
    performance_results: list[PerformanceResult],
    metadata: RunMetadata,
    regressions: list[dict[str, Any]] | None = None,
) -> QualityReport:
    rules = _profile(gate_config, profile)
    by_metric: dict[str, list[EvaluationResult]] = defaultdict(list)
    for result in results:
        by_metric[result.metric].append(result)

    blocking: list[EvaluationResult] = []
    summary: dict[str, str] = {}
    completed_suites = {
        str(result.metadata.get("suite"))
        for result in results
        if result.metric == "suite_completed" and result.passed and result.metadata.get("suite")
    }
    missing_suites = [
        suite for suite in rules.get("required_suites", []) if suite not in completed_suites
    ]
    summary["suite_completeness"] = "FAIL" if missing_suites else "PASS"
    for suite in missing_suites:
        blocking.append(
            EvaluationResult(
                test_id=f"suite:{suite}",
                framework="quality-gate",
                category="suite_completeness",
                metric="required_suite",
                passed=False,
                blocking=True,
                reason=f"Required suite '{suite}' did not produce completion evidence.",
            )
        )
    for result in results:
        if result.blocking and not result.passed and result.metric != "suite_completed":
            blocking.append(result)
    quality_failed = False
    for metric, rule in rules.get("quality", {}).items():
        metric_results = by_metric.get(metric, [])
        if not metric_results:
            summary[metric] = "SKIP"
            continue
        scores = [item.score for item in metric_results if item.score is not None]
        value = (
            mean(scores)
            if scores
            else sum(item.passed for item in metric_results) / len(metric_results)
        )
        passed = value >= float(rule["min"])
        summary[metric] = "PASS" if passed else "FAIL"
        if not passed and rule.get("blocking", True):
            quality_failed = True
            blocking.append(
                EvaluationResult(
                    test_id=f"aggregate:{metric}",
                    framework="quality-gate",
                    category="quality",
                    metric=metric,
                    score=value,
                    threshold=float(rule["min"]),
                    passed=False,
                    blocking=True,
                    reason="Aggregate metric is below the configured threshold.",
                )
            )

    severity_counts = {severity.value: 0 for severity in Severity}
    for finding in security_findings:
        if finding.severity:
            severity_counts[finding.severity.value] += 1
    security_rules = rules.get("security", {})
    security_failed = severity_counts["critical"] > security_rules.get(
        "max_critical", 999
    ) or severity_counts["high"] > security_rules.get("max_high", 999)
    summary["security"] = "FAIL" if security_failed else "PASS"
    if security_failed:
        for finding in security_findings:
            if finding.severity in {Severity.CRITICAL, Severity.HIGH}:
                blocking.append(
                    EvaluationResult(
                        test_id=finding.id,
                        framework=finding.framework,
                        category="security",
                        metric=finding.category,
                        passed=False,
                        severity=finding.severity,
                        blocking=True,
                        reason=finding.result,
                    )
                )

    performance_failed = any(not item.passed for item in performance_results)
    summary["performance"] = (
        "FAIL" if performance_failed else "PASS" if performance_results else "SKIP"
    )
    for item in performance_results:
        if not item.passed:
            blocking.append(
                EvaluationResult(
                    test_id=f"performance:{item.scenario}",
                    framework="aiperf",
                    category="performance",
                    metric=item.metric,
                    passed=False,
                    blocking=True,
                    reason=f"{item.value} {item.unit} violates threshold {item.threshold}",
                )
            )

    regression_items = regressions or []
    regression_failed = any(
        item.get("classification") == "blocking_regression" for item in regression_items
    )
    summary["regression"] = "FAIL" if regression_failed else "PASS" if regression_items else "SKIP"

    failed = (
        bool(blocking)
        or bool(missing_suites)
        or quality_failed
        or security_failed
        or performance_failed
        or regression_failed
    )
    return QualityReport(
        status="FAIL" if failed else "PASS",
        profile=profile,
        summary=summary,  # type: ignore[arg-type]
        blocking_failures=blocking,
        results=results,
        security_findings=security_findings,
        performance_results=performance_results,
        regressions=regression_items,
        metadata=metadata,
    )
