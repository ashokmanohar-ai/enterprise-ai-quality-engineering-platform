PYTHON ?= python
PROFILE ?= dev

.PHONY: setup validate test-unit test-llm test-rag test-prompts test-agents test-mcp test-security test-embeddings test-performance test-pr test-all report quality-gate

setup:
	$(PYTHON) -m venv .venv
	.venv/bin/python -m pip install --upgrade pip
	.venv/bin/python -m pip install -e '.[dev,llm,rag,mcp]'
	npm ci

validate:
	$(PYTHON) -m ai_quality.cli validate

test-unit:
	$(PYTHON) -m pytest tests/unit

test-llm:
	bash scripts/test_llm.sh $(PROFILE)

test-rag:
	bash scripts/test_rag.sh $(PROFILE)

test-prompts:
	bash scripts/test_prompts.sh $(PROFILE)

test-agents:
	$(PYTHON) -m pytest tests/agents

test-mcp:
	$(PYTHON) -m pytest tests/mcp

test-security:
	bash scripts/test_security.sh $(PROFILE) security

test-embeddings:
	bash scripts/test_embeddings.sh $(PROFILE)

test-performance:
	bash scripts/test_performance.sh $(PROFILE)

test-pr:
	bash scripts/run_all.sh pr

test-all:
	bash scripts/run_all.sh $(PROFILE)

report:
	$(PYTHON) -m ai_quality.cli report

quality-gate:
	$(PYTHON) -m ai_quality.cli gate --profile $(PROFILE)
