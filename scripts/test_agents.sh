#!/usr/bin/env bash
set -euo pipefail
python -m pytest tests/agents
python scripts/mark_suite.py agent
