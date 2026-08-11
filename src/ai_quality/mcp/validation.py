from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ai_quality.applications.agent_app import SupportTools


@dataclass(frozen=True)
class ContractCheck:
    name: str
    passed: bool
    reason: str


EXPECTED_TOOLS: dict[str, set[str]] = {
    "search_company_policy": {"query"},
    "get_refund_policy": set(),
    "get_subscription_status": {"account_id", "requester_account_id"},
    "create_support_ticket": {"subject", "description", "authorized"},
}


def validate_business_rules() -> list[ContractCheck]:
    forbidden = SupportTools.get_subscription_status("acct-200", "acct-100")
    unconfirmed = SupportTools.create_support_ticket("test", "test", authorized=False)
    refund = SupportTools.get_refund_policy()
    return [
        ContractCheck(
            "cross-account access blocked", forbidden.get("error") == "forbidden", str(forbidden)
        ),
        ContractCheck(
            "ticket confirmation required",
            unconfirmed.get("error") == "confirmation_required",
            str(unconfirmed),
        ),
        ContractCheck(
            "refund source returned", refund.get("source") == "refund-policy.md", str(refund)
        ),
    ]


def validate_tool_schema(tool: dict[str, Any]) -> ContractCheck:
    name = str(tool.get("name", ""))
    schema = tool.get("inputSchema") or tool.get("input_schema") or {}
    required = set(schema.get("required", []))
    expected = EXPECTED_TOOLS.get(name)
    if expected is None:
        return ContractCheck(name, False, "Unexpected tool")
    return ContractCheck(
        name,
        required <= expected and schema.get("type") == "object",
        f"required={sorted(required)}",
    )
