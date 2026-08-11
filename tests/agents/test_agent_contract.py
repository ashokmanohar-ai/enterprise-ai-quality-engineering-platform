import pytest

from ai_quality.evaluation.agent_runner import evaluate_agent_case
from ai_quality.evaluation.datasets import load_jsonl

AGENT_CASES = [
    case for case in load_jsonl("datasets/agents/agent-cases.jsonl") if case.category == "agent"
]


@pytest.mark.parametrize("case", AGENT_CASES, ids=lambda item: item.id)
def test_agent_case(case) -> None:  # type: ignore[no-untyped-def]
    results = evaluate_agent_case(case)
    assert all(result.passed for result in results), [
        (item.metric, item.reason) for item in results if not item.passed
    ]
