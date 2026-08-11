# Datasets

## Canonical schema

`CanonicalCase` contains `id`, category, input, reference answer, contexts, expected behavior, tags, criticality, and metadata. Expected behavior supports required/forbidden claims, expected/forbidden tools, maximum tool calls, and JSON schema.

Directories:

- `golden`: 30 normal, edge, RAG, hallucination, structured, business-rule, and historical cases;
- `agents`: 15 tool/authorization/confirmation/loop/MCP cases;
- `security`: 20 synthetic adversarial regressions;
- `embeddings`: application retrieval examples;
- `performance`: reusable AIPerf input;
- `generated`: derived native formats.

## Adapter policy

DeepEval receives input, actual output, expected output, context, and retrieval context. Ragas 0.4 receives `user_input`, `response`, `reference`, `retrieved_contexts`, and `reference_contexts`. Promptfoo receives vars and assertions. Phoenix/Langfuse experiments receive the canonical ID and run metadata. PyRIT consumes the separate adversarial objectives rather than normal golden cases unless reproducing a confirmed case.

Run `python scripts/export_datasets.py` after changing canonical data. Review the diff, but never edit the generated file directly.

## Production defect promotion

1. Locate the interaction by correlation/trace ID.
2. Identify the failure and affected quality dimension.
3. Remove names, addresses, account identifiers, secrets, proprietary text, and unnecessary prompt content.
4. Replace them with synthetic equivalents.
5. Add expected behavior and criticality.
6. Reproduce the defect before fixing it.
7. Retain the case permanently after the fix.

Raw production interactions are not evaluation data until sanitized and approved.
