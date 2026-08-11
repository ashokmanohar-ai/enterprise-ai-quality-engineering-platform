#!/usr/bin/env bash
set -euo pipefail
python -m pytest tests/mcp
npx @modelcontextprotocol/inspector --cli python -m ai_quality.mcp.server --method tools/list > reports/raw/mcp-tools.json
python scripts/mark_suite.py mcp
