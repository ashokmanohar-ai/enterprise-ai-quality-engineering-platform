# CI/CD quality gates

## Pull request

Checkout → lint/deterministic → DeepEval subset → Ragas subset → Promptfoo regression → agent/MCP → security regression smoke → normalize → gate → upload short-retention evidence.

Changed-file routing in `scripts/select_changed_suites.py` expands the depth of relevant PR checks: prompt changes route to larger LLM/Promptfoo samples; retriever/KB changes to larger Ragas samples; agent/MCP changes to agent/MCP/security smoke; security policy changes to an authorized native smoke scan. Deterministic tests and every profile-required suite still run. Unselected model-mediated suites use five-case canaries and selected suites use the configured PR maximum, so path selection saves cost without converting required evidence into a skip.

## Nightly

Protected security environment runs Promptfoo red-team, PyRIT campaigns, and scoped Garak. Protected performance environment runs AIPerf load. Expanded LLM/RAG, embedding, and full golden evaluations should run on the nightly matrix. Raw security artifacts remain private with short retention.

## Release

Run every required suite, compare production baseline/candidate, and then call one gate. Missing suite markers fail. Configure GitHub environments with reviewers for security, performance, and release. Use least-privilege secrets and prevent forked PRs from receiving them.

## Gate behavior

The gate reads normalized JSONL, config thresholds, internal severity policy, performance SLOs, baseline deltas, and completion markers. It writes JSON/Markdown and exits nonzero on block. Do not use average-only release decisions.

Required repository settings: branch protection, required PR workflow, protected environment approvals, Dependabot/Renovate review, secret scanning, code scanning, and artifact retention appropriate to data classification.
