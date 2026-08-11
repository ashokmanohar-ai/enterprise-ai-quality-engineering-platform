# Agent testing

Agent quality is trajectory quality plus final-answer quality.

Deterministic checks assert:

- correct tool selection and absence of forbidden tools;
- correct account IDs and argument types;
- business-rule/permission enforcement;
- maximum tool-call count and loop prevention;
- explicit confirmation before state-changing tools;
- final answer consistency with tool results;
- no tool-use hallucination.

DeepEval adds model-mediated task completion, tool correctness, argument correctness, and step efficiency when a live trajectory is available. Phoenix/Langfuse captures planning/orchestration, tool call, tool result, additional calls, and final generation.

Troubleshoot wrong tool, bad arguments, repeats/loops, timeout, ignored result, contradictory final answer, unauthorized use, and hallucinated tools independently. A polished answer is not a passing agent result if the trajectory violated policy.

Run `make test-agents`. The offline reference agent is deterministic so PR business-rule evidence remains fast and inexpensive.
