#!/usr/bin/env bash
set -euo pipefail
python -m pytest tests/unit
python scripts/mark_suite.py deterministic
