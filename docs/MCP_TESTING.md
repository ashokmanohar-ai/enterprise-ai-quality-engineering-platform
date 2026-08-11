# MCP testing

The server uses the stable MCP Python SDK v2 and the 2026-07-28 protocol line. It exposes four tools, two resources, and one prompt. The same synthetic business functions power the non-MCP agent.

Tools: `search_company_policy`, `get_refund_policy`, `get_subscription_status`, `create_support_ticket`.

Inspector 2.0 is a single package with Web, CLI, and TUI clients:

```bash
npx @modelcontextprotocol/inspector python -m ai_quality.mcp.server
npx @modelcontextprotocol/inspector --tui python -m ai_quality.mcp.server
npx @modelcontextprotocol/inspector --cli python -m ai_quality.mcp.server --method tools/list
```

Inspect connection, discovery, input schemas, calls, resources, prompts, protocol traffic, and errors. Inspector accelerates development; it is not a replacement for automated contract/business tests.

CI tests startup/discovery, schema object types, required arguments, valid and invalid calls, error behavior, cross-account denial, ticket confirmation, resource content, prompt retrieval, and agent interpretation.

Troubleshoot server unavailable, invalid schema, execution exception, incorrect resource, invalid arguments, business-rule violation, and agent misinterpretation separately. Log to stderr for stdio; stdout belongs to protocol messages.
