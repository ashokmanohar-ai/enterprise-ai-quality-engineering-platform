from __future__ import annotations

import pytest

from ai_quality.applications.base import (
    AUTRequest,
    CustomerSupportAUT,
    RAGAssistantAUT,
    SupportAgentAUT,
)


@pytest.mark.asyncio
async def test_shared_aut_contract_covers_llm_rag_and_agent() -> None:
    context = ["Standard refunds are available within 30 days."]
    llm = await CustomerSupportAUT().invoke(AUTRequest("What is the refund window?", context))
    rag = await RAGAssistantAUT().invoke(AUTRequest("What is the refund policy?"))
    agent = await SupportAgentAUT().invoke(AUTRequest("What is the refund policy?"))

    assert "30 days" in llm.output
    assert rag.contexts and rag.sources
    assert agent.tool_calls[0]["name"] == "get_refund_policy"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_same_contract_wraps_mcp_agent() -> None:
    pytest.importorskip("mcp")
    from ai_quality.applications.base import MCPSupportAgentAUT

    result = await MCPSupportAgentAUT().invoke(AUTRequest("Use MCP to get the refund policy."))
    assert result.tool_calls[0]["name"] == "get_refund_policy"
    assert "30 days" in result.output
