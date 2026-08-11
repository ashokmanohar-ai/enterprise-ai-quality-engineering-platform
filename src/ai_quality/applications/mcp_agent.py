from __future__ import annotations

from typing import Any

from ai_quality.applications.agent_app import AgentResult, ToolCall
from ai_quality.mcp.server import build_server
from ai_quality.observability.telemetry import content_attributes, get_backend


def _payload(structured_content: dict[str, Any] | None) -> dict[str, Any]:
    content = structured_content or {}
    result = content.get("result")
    return result if isinstance(result, dict) else content


class MCPEnabledSupportAgent:
    """Deterministic policy agent whose operations cross the real MCP protocol boundary."""

    def __init__(self, backend=None) -> None:  # type: ignore[no-untyped-def]
        self.backend = backend or get_backend()

    async def run(
        self,
        request: str,
        *,
        requester_account_id: str = "acct-100",
        confirmed: bool = False,
    ) -> AgentResult:
        try:
            from mcp import Client
        except ImportError as exc:
            raise RuntimeError("Install the MCP runtime with: pip install -e '.[mcp]'") from exc

        with self.backend.span("agent_request", attributes=content_attributes("input", request)):
            with self.backend.span("planning", attributes={"request.length": len(request)}):
                lowered = request.lower()
                if "refund" in lowered:
                    name, arguments = "get_refund_policy", {}
                elif "subscription" in lowered or "plan" in lowered:
                    target = (
                        "acct-200"
                        if "acct-200" in lowered or "other customer" in lowered
                        else requester_account_id
                    )
                    name = "get_subscription_status"
                    arguments = {
                        "account_id": target,
                        "requester_account_id": requester_account_id,
                    }
                elif "ticket" in lowered:
                    name = "create_support_ticket"
                    arguments = {
                        "subject": "Customer request",
                        "description": request,
                        "authorized": confirmed,
                    }
                else:
                    name, arguments = "search_company_policy", {"query": request}
            async with Client(build_server(), mode="2026-07-28") as client:
                with self.backend.span(
                    "tool_call",
                    attributes={"tool.name": name, "tool.argument_count": len(arguments)},
                ):
                    native = await client.call_tool(name, arguments)
            payload = _payload(native.structured_content)
            with self.backend.span(
                "tool_result",
                attributes={"tool.name": name, "tool.error": str(payload.get("error", ""))},
            ):
                pass
            call = ToolCall(name=name, arguments=arguments, result=payload)
            if payload.get("error"):
                result = AgentResult(
                    payload.get("message", payload["error"]),
                    [call],
                    completed=False,
                    blocked_reason=payload["error"],
                )
            else:
                if name == "get_refund_policy":
                    answer = str(payload["policy"])
                elif name == "get_subscription_status":
                    answer = (
                        f"Your subscription is {payload.get('status')} "
                        f"on the {payload.get('plan')} plan."
                    )
                elif name == "create_support_ticket":
                    answer = f"Created {payload['ticket_id']}."
                else:
                    answer = (
                        "I found no matching policy."
                        if not payload.get("count")
                        else str(payload["matches"])
                    )
                result = AgentResult(answer, [call])
            with self.backend.span(
                "final_generation",
                attributes={
                    **content_attributes("output", result.final_answer),
                    "tool.call_count": len(result.tool_calls),
                    "task.completed": result.completed,
                },
            ):
                return result
