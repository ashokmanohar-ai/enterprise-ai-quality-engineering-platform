# MCP Inspector v2

Web: `npx @modelcontextprotocol/inspector python -m ai_quality.mcp.server`

TUI: `npx @modelcontextprotocol/inspector --tui python -m ai_quality.mcp.server`

CI list: `npx @modelcontextprotocol/inspector --cli python -m ai_quality.mcp.server --method tools/list`

Repeat `--method` with `resources/list`, `prompts/list`, and `tools/call`. Inspector is a development and troubleshooting client; pytest contract and business-rule tests remain the automated release evidence.
