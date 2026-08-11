from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from ai_quality.observability.telemetry import content_attributes, get_backend


@dataclass(frozen=True)
class ToolCall:
    name: str
    arguments: dict[str, Any]
    result: dict[str, Any]


@dataclass(frozen=True)
class AgentResult:
    final_answer: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    completed: bool = True
    blocked_reason: str | None = None


class SupportTools:
    """Synthetic, side-effect-free tools shared by the local agent and MCP server."""

    policies = {
        "refund": "Standard refunds are available within 30 days of the initial purchase.",
        "cancellation": (
            "Cancellation stops the next renewal; current access remains until period end."
        ),
        "deletion": "Account deletion requires owner verification and completes within 30 days.",
    }
    subscriptions = {
        "acct-100": {"status": "active", "plan": "business", "renewal": "2026-09-01"},
        "acct-200": {"status": "past_due", "plan": "starter", "renewal": "2026-08-15"},
    }

    @classmethod
    def search_company_policy(cls, query: str) -> dict[str, Any]:
        matches = {name: value for name, value in cls.policies.items() if name in query.lower()}
        return {"matches": matches, "count": len(matches)}

    @classmethod
    def get_refund_policy(cls) -> dict[str, Any]:
        return {"policy": cls.policies["refund"], "source": "refund-policy.md"}

    @classmethod
    def get_subscription_status(cls, account_id: str, requester_account_id: str) -> dict[str, Any]:
        if account_id != requester_account_id:
            return {
                "error": "forbidden",
                "message": "A customer may only access their own subscription.",
            }
        return cls.subscriptions.get(account_id, {"error": "not_found"})

    @staticmethod
    def create_support_ticket(
        subject: str, description: str, authorized: bool = False
    ) -> dict[str, Any]:
        if not authorized:
            return {
                "error": "confirmation_required",
                "message": "Explicit user confirmation is required.",
            }
        return {
            "ticket_id": "TICKET-SYNTHETIC-001",
            "status": "created",
            "subject": subject,
            "description": description,
        }


class DeterministicSupportAgent:
    def __init__(self, backend=None) -> None:  # type: ignore[no-untyped-def]
        self.backend = backend or get_backend()
        self.tools: dict[str, Callable[..., dict[str, Any]]] = {
            "search_company_policy": SupportTools.search_company_policy,
            "get_refund_policy": SupportTools.get_refund_policy,
            "get_subscription_status": SupportTools.get_subscription_status,
            "create_support_ticket": SupportTools.create_support_ticket,
        }

    def _call(self, name: str, **arguments: Any) -> ToolCall:
        with self.backend.span(
            "tool_call", attributes={"tool.name": name, "tool.argument_count": len(arguments)}
        ):
            result = self.tools[name](**arguments)
        with self.backend.span(
            "tool_result",
            attributes={"tool.name": name, "tool.error": str(result.get("error", ""))},
        ):
            pass
        return ToolCall(name, arguments, result)

    def _finish(self, result: AgentResult) -> AgentResult:
        attributes = {
            **content_attributes("output", result.final_answer),
            "tool.call_count": len(result.tool_calls),
            "task.completed": result.completed,
        }
        with self.backend.span("final_generation", attributes=attributes):
            return result

    def run(
        self, request: str, *, requester_account_id: str = "acct-100", confirmed: bool = False
    ) -> AgentResult:
        with self.backend.span("agent_request", attributes=content_attributes("input", request)):
            with self.backend.span("planning", attributes={"request.length": len(request)}):
                lowered = request.lower()
                if "other customer" in lowered or (
                    "acct-200" in lowered and requester_account_id != "acct-200"
                ):
                    intent = "cross_account_subscription"
                elif "refund" in lowered:
                    intent = "refund"
                elif "subscription" in lowered or "plan" in lowered:
                    intent = "subscription"
                elif "ticket" in lowered:
                    intent = "ticket"
                else:
                    intent = "policy_search"
            if intent == "cross_account_subscription":
                call = self._call(
                    "get_subscription_status",
                    account_id="acct-200",
                    requester_account_id=requester_account_id,
                )
                return self._finish(
                    AgentResult(
                        call.result["message"],
                        [call],
                        completed=False,
                        blocked_reason="authorization",
                    )
                )
            if intent == "refund":
                call = self._call("get_refund_policy")
                return self._finish(AgentResult(call.result["policy"], [call]))
            if intent == "subscription":
                call = self._call(
                    "get_subscription_status",
                    account_id=requester_account_id,
                    requester_account_id=requester_account_id,
                )
                return self._finish(
                    AgentResult(
                        f"Your subscription is {call.result.get('status')} "
                        f"on the {call.result.get('plan')} plan.",
                        [call],
                    )
                )
            if intent == "ticket":
                call = self._call(
                    "create_support_ticket",
                    subject="Customer request",
                    description=request,
                    authorized=confirmed,
                )
                answer = (
                    str(call.result["message"])
                    if "message" in call.result
                    else f"Created {call.result['ticket_id']}."
                )
                return self._finish(
                    AgentResult(
                        answer,
                        [call],
                        completed=confirmed,
                        blocked_reason=None if confirmed else "confirmation",
                    )
                )
            call = self._call("search_company_policy", query=request)
            return self._finish(
                AgentResult(
                    "I found no matching policy."
                    if not call.result["count"]
                    else str(call.result["matches"]),
                    [call],
                )
            )
