import pytest

from ai_quality.config import get_settings
from ai_quality.evaluation.datasets import load_jsonl
from ai_quality.evaluation.deepeval_runner import AzureDeepEvalJudge
from ai_quality.evaluation.thresholds import quality_threshold


@pytest.mark.llm
def test_agent_trajectory_with_deepeval() -> None:
    settings = get_settings()
    if not settings.aiq_allow_live_model_calls:
        pytest.skip("Live evaluator calls disabled")
    from deepeval import assert_test
    from deepeval.dataset import Golden
    from deepeval.metrics import StepEfficiencyMetric, TaskCompletionMetric
    from deepeval.tracing import observe, update_current_trace

    from ai_quality.applications.agent_app import DeterministicSupportAgent

    case = load_jsonl("datasets/agents/agent-cases.jsonl", limit=1)[0]

    @observe(type="agent")
    def traced_agent(query: str) -> str:
        output = DeterministicSupportAgent().run(query).final_answer
        update_current_trace(input=query, output=output)
        return output

    traced_agent(case.input)
    judge = AzureDeepEvalJudge.build(settings)
    assert_test(
        golden=Golden(input=case.input, expected_output=case.reference_answer),
        metrics=[
            TaskCompletionMetric(
                threshold=quality_threshold("agent_task_completion", "pr", 0.9), model=judge
            ),
            StepEfficiencyMetric(
                threshold=quality_threshold("step_efficiency", "pr", 0.85), model=judge
            ),
        ],
    )
