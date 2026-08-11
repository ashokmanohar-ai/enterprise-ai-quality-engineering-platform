from __future__ import annotations

from ai_quality.applications.agent_app import SupportTools

try:
    from mcp.server import MCPServer
except ImportError:  # Core PR profile does not require optional MCP runtime.
    MCPServer = None  # type: ignore[assignment,misc]


def build_server():  # type: ignore[no-untyped-def]
    if MCPServer is None:
        raise RuntimeError("Install the MCP runtime with: pip install -e '.[mcp]'")
    server = MCPServer("AcmeCloud Support MCP")

    @server.tool()
    def search_company_policy(query: str) -> dict[str, object]:
        """Search public synthetic company policies."""
        return SupportTools.search_company_policy(query)

    @server.tool()
    def get_refund_policy() -> dict[str, object]:
        """Return the current synthetic refund policy."""
        return SupportTools.get_refund_policy()

    @server.tool()
    def get_subscription_status(account_id: str, requester_account_id: str) -> dict[str, object]:
        """Read a subscription only when requester and target account match."""
        return SupportTools.get_subscription_status(account_id, requester_account_id)

    @server.tool()
    def create_support_ticket(
        subject: str, description: str, authorized: bool = False
    ) -> dict[str, object]:
        """Create a synthetic ticket; explicit confirmation is mandatory."""
        return SupportTools.create_support_ticket(subject, description, authorized)

    @server.resource("policy://company/refund")
    def refund_resource() -> str:
        """AcmeCloud refund policy."""
        return SupportTools.policies["refund"]

    @server.resource("product://acmecloud/support")
    def product_resource() -> str:
        """AcmeCloud support product information."""
        return "AcmeCloud is a fictional multi-tenant SaaS platform used only for tests."

    @server.prompt()
    def support_answer(question: str) -> str:
        """Create a grounded customer-support prompt."""
        return f"Answer this AcmeCloud question from discovered policy resources only: {question}"

    return server


def main() -> None:
    build_server().run(transport="stdio")


if __name__ == "__main__":
    main()
