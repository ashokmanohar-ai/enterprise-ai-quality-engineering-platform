#!/usr/bin/env bash
set -euo pipefail
: "${AIQ_SECURITY_AUTHORIZED:?Set AIQ_SECURITY_AUTHORIZED=true only with written target authorization}"
python -m ai_quality.cli run --profile "${1:-nightly}" --suite security
python scripts/mark_suite.py "${2:-security}"
