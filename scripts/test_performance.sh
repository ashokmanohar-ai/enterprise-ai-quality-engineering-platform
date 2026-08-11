#!/usr/bin/env bash
set -euo pipefail
: "${AIQ_PERFORMANCE_AUTHORIZED:?Set AIQ_PERFORMANCE_AUTHORIZED=true only with target-owner authorization}"
python -m ai_quality.cli run --profile "${1:-nightly}" --suite performance
python scripts/mark_suite.py performance
