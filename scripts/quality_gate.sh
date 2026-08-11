#!/usr/bin/env bash
set -euo pipefail
python -m ai_quality.cli report --profile "${1:-pr}"
python -m ai_quality.cli gate --profile "${1:-pr}"
