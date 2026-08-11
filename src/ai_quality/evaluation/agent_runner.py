from __future__ import annotations

from ai_quality.applications.agent_app import AgentResult, DeterministicSupportAgent
from ai_quality.applications.mcp_agent import MCPEnabledSupportAgent
from ai_quality.evaluation.contracts import CanonicalCase, EvaluationResult


def normalize_agent_result(case: CanonicalCase, result: AgentResult) -> list[EvaluationResult]:
    calls = [call.name for call in result.tool_calls]
    expected = case.expected_behavior.expected_tools
    forbidden = case.expected_behavior.forbidden_tools
    selection_passed = all(tool in calls for tool in expected) and not any(
        tool in calls for tool in forbidden
    )
    count_passed = (
        case.expected_behavior.max_tool_calls is None
        or len(calls) <= case.expected_behavior.max_tool_calls
    )
    content_passed = all(
        value.lower() in result.final_answer.lower()
        for value in case.expected_behavior.must_include
    )
    content_passed = content_passed and not any(
        value.lower() in result.final_answer.lower()
        for value in case.expected_behavior.must_not_claim
    )
    return [
        EvaluationResult(
            test_id=case.id,
            framework="custom",
            category="agent",
            metric="tool_selection",
            score=1.0 if selection_passed else 0.0,
            threshold=1.0,
            passed=selection_passed,
            reason=f"calls={calls}",
        ),
        EvaluationResult(
            test_id=case.id,
            framework="custom",
            category="agent",
            metric="tool_call_efficiency",
            score=1.0 if count_passed else 0.0,
            threshold=1.0,
            passed=count_passed,
            reason=f"tool_call_count={len(calls)}",
        ),
        EvaluationResult(
            test_id=case.id,
            framework="custom",
            category="agent",
            metric="agent_task_completion",
            score=1.0
            if content_passed and (result.completed or case.metadata.get("expect_blocked"))
            else 0.0,
            threshold=1.0,
            passed=bool(
                content_passed and (result.completed or case.metadata.get("expect_blocked"))
            ),
            reason=result.blocked_reason or result.final_answer,
        ),
    ]


def evaluate_agent_case(
    case: CanonicalCase, agent: DeterministicSupportAgent | None = None
) -> list[EvaluationResult]:
    runner = agent or DeterministicSupportAgent()
    result = runner.run(case.input, confirmed=bool(case.metadata.get("confirmed", False)))
    return normalize_agent_result(case, result)


async def evaluate_mcp_agent_case(
    case: CanonicalCase, agent: MCPEnabledSupportAgent | None = None
) -> list[EvaluationResult]:
    runner = agent or MCPEnabledSupportAgent()
    result = await runner.run(case.input, confirmed=bool(case.metadata.get("confirmed", False)))
    return normalize_agent_result(case, result)
