from ai_quality.config import load_yaml
from ai_quality.evaluation.contracts import EvaluationResult, RunMetadata
from ai_quality.reporting.quality_gate import evaluate_gate
from ai_quality.reporting.render import write_report


def test_report_is_written(tmp_path) -> None:  # type: ignore[no-untyped-def]
    report = evaluate_gate(
        profile="dev",
        gate_config=load_yaml("config/quality-gates.yaml"),
        results=[
            EvaluationResult(
                test_id="x",
                framework="custom",
                category="quality",
                metric="faithfulness",
                score=1.0,
                threshold=0.75,
                passed=True,
            )
        ],
        security_findings=[],
        performance_results=[],
        metadata=RunMetadata(evaluation_run_id="test", dataset_version="v1", prompt_version="v2"),
    )
    json_path, markdown_path = write_report(report, tmp_path)
    assert json_path.exists() and markdown_path.exists()
    assert "Deployment decision" in markdown_path.read_text(encoding="utf-8")
