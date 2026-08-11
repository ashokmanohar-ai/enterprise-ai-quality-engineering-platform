#!/usr/bin/env bash
set -euo pipefail
python -m ai_quality.cli run --profile "${1:-pr}" --suite rag
