from ai_quality.config import load_yaml
from ai_quality.evaluation.contracts import EvaluationResult, RunMetadata, SecurityFinding, Severity
from ai_quality.reporting.quality_gate import evaluate_gate


def metadata() -> RunMetadata:
    return RunMetadata(evaluation_run_id="test", dataset_version="test", prompt_version="v2")


def test_gate_blocks_high_security_finding() -> None:
    report = evaluate_gate(
        profile="pr",
        gate_config=load_yaml("config/quality-gates.yaml"),
        results=[],
        security_findings=[
            SecurityFinding(
                id="f-1",
                framework="garak",
                category="prompt_injection",
                severity=Severity.HIGH,
                input="synthetic",
                result="hit",
                blocking=True,
            )
        ],
        performance_results=[],
        metadata=metadata(),
    )
    assert report.status == "FAIL"
    assert report.summary["security"] == "FAIL"


def test_gate_does_not_hide_critical_case_behind_average() -> None:
    results = [
        EvaluationResult(
            test_id="critical-1",
            framework="custom",
            category="quality",
            metric="faithfulness",
            score=0.0,
            threshold=0.8,
            passed=False,
            blocking=True,
        )
    ]
    report = evaluate_gate(
        profile="pr",
        gate_config=load_yaml("config/quality-gates.yaml"),
        results=results,
        security_findings=[],
        performance_results=[],
        metadata=metadata(),
    )
    assert report.status == "FAIL"
