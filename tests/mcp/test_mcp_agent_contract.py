from __future__ import annotations

import pytest

pytest.importorskip("mcp")

from ai_quality.evaluation.agent_runner import evaluate_mcp_agent_case
from ai_quality.evaluation.datasets import load_jsonl

MCP_CASES = [
    case for case in load_jsonl("datasets/agents/agent-cases.jsonl") if case.category == "mcp"
]


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize("case", MCP_CASES, ids=lambda item: item.id)
async def test_mcp_enabled_agent_case(case) -> None:  # type: ignore[no-untyped-def]
    results = await evaluate_mcp_agent_case(case)
    assert all(result.passed for result in results), [
        (item.metric, item.reason) for item in results if not item.passed
    ]
