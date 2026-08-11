from __future__ import annotations

import pytest

pytest.importorskip("mcp")

from ai_quality.applications.mcp_agent import MCPEnabledSupportAgent
from ai_quality.mcp.server import build_server
from mcp import Client


def _items(response, name: str):  # type: ignore[no-untyped-def]
    return getattr(response, name, response)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_discovery_and_generated_input_schemas() -> None:
    async with Client(build_server(), mode="2026-07-28") as client:
        tools = _items(await client.list_tools(), "tools")
        resources = _items(await client.list_resources(), "resources")
        prompts = _items(await client.list_prompts(), "prompts")
    by_name = {tool.name: tool for tool in tools}
    assert set(by_name) == {
        "search_company_policy",
        "get_refund_policy",
        "get_subscription_status",
        "create_support_ticket",
    }
    assert all(tool.input_schema["type"] == "object" for tool in tools)
    assert "account_id" in by_name["get_subscription_status"].input_schema["required"]
    assert len(resources) == 2
    assert [prompt.name for prompt in prompts] == ["support_answer"]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_valid_calls_and_business_rule_errors_are_model_visible() -> None:
    async with Client(build_server(), mode="2026-07-28") as client:
        refund = await client.call_tool("get_refund_policy", {})
        forbidden = await client.call_tool(
            "get_subscription_status",
            {"account_id": "acct-200", "requester_account_id": "acct-100"},
        )
        confirmation = await client.call_tool(
            "create_support_ticket",
            {"subject": "Synthetic", "description": "Synthetic test"},
        )
    assert _payload(refund)["source"] == "refund-policy.md"
    assert _payload(forbidden)["error"] == "forbidden"
    assert _payload(confirmation)["error"] == "confirmation_required"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_invalid_arguments_are_rejected_by_generated_schema() -> None:
    async with Client(build_server(), mode="2026-07-28") as client:
        result = await client.call_tool("get_subscription_status", {"account_id": 17})
    assert result.is_error is True


@pytest.mark.asyncio
@pytest.mark.integration
async def test_resource_prompt_and_agent_interpretation() -> None:
    async with Client(build_server(), mode="2026-07-28") as client:
        resource = await client.read_resource("policy://company/refund")
        prompt = await client.get_prompt(
            "support_answer", {"question": "What is the refund window?"}
        )
    assert "30 days" in str(resource)
    assert "refund window" in str(prompt).lower()
    result = await MCPEnabledSupportAgent().run("What is the refund policy?")
    assert result.completed is True
    assert [call.name for call in result.tool_calls] == ["get_refund_policy"]
    assert "30 days" in result.final_answer


def _payload(result):  # type: ignore[no-untyped-def]
    content = result.structured_content or {}
    nested = content.get("result")
    return nested if isinstance(nested, dict) else content
