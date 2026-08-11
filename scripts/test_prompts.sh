#!/usr/bin/env bash
set -euo pipefail
profile="${1:-pr}"
if [[ "$profile" == "nightly" || "$profile" == "release" ]]; then
  python scripts/export_datasets.py
fi
python -m ai_quality.cli run --profile "$profile" --suite prompt_regression
