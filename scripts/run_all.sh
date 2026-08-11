#!/usr/bin/env bash
set -euo pipefail
profile="${1:-dev}"
bash scripts/test_unit.sh
bash scripts/test_agents.sh
bash scripts/test_mcp.sh
if [[ "$profile" == "dev" ]]; then
  AIQ_MAX_EVALUATION_CASES="${AIQ_MAX_EVALUATION_CASES:-10}" bash scripts/test_llm.sh "$profile"
  AIQ_MAX_EVALUATION_CASES="${AIQ_MAX_EVALUATION_CASES:-10}" bash scripts/test_rag.sh "$profile"
else
  bash scripts/test_llm.sh "$profile"
  bash scripts/test_rag.sh "$profile"
  bash scripts/test_prompts.sh "$profile"
fi
python -m ai_quality.cli gate --profile "$profile"
