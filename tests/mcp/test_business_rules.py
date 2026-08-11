from ai_quality.applications.agent_app import SupportTools
from ai_quality.mcp.validation import EXPECTED_TOOLS, validate_business_rules, validate_tool_schema


def test_all_business_rules() -> None:
    assert all(check.passed for check in validate_business_rules())


def test_tool_contract_is_explicit() -> None:
    assert set(EXPECTED_TOOLS) == {
        "search_company_policy",
        "get_refund_policy",
        "get_subscription_status",
        "create_support_ticket",
    }


def test_invalid_cross_account_input_returns_forbidden() -> None:
    assert SupportTools.get_subscription_status("acct-200", "acct-100")["error"] == "forbidden"


def test_ticket_requires_confirmation() -> None:
    assert SupportTools.create_support_ticket("x", "y")["error"] == "confirmation_required"


def test_schema_requires_object() -> None:
    check = validate_tool_schema({"name": "get_refund_policy", "inputSchema": {"type": "string"}})
    assert check.passed is False
