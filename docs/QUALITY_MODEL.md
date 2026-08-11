# Quality model

Quality is a set of independently governed dimensions, not a single score.

| Dimension | Question | Primary evidence |
|---|---|---|
| Functional correctness | Did required behavior and business rules hold? | deterministic assertions, DeepEval |
| Relevance | Did the response address intent? | DeepEval/Ragas |
| Groundedness | Are claims supported by retrieved evidence? | DeepEval faithfulness, Ragas faithfulness |
| Retrieval | Were required chunks found and ranked well? | Ragas context precision/recall |
| Prompt stability | Did a prompt change break cases? | Promptfoo baseline/candidate |
| Agent reliability | Correct tools, arguments, sequence, completion? | deterministic trajectory checks, DeepEval |
| MCP quality | Valid protocol surface and safe business behavior? | Inspector + pytest |
| Security | Did adversarial input cause prohibited behavior? | Promptfoo, PyRIT, Garak |
| Embedding quality | Does a candidate retrieve relevant evidence? | MTEB + application benchmark + Ragas |
| Performance | Does the live endpoint meet the configured SLO? | AIPerf |
| Operability | Can a failure be correlated and diagnosed? | Phoenix/Langfuse traces and scores |

## Decision rules

Scores are normalized to higher-is-better where possible. Native values remain in metadata. Thresholds are profile-specific. A result can be explicitly `blocking`; critical business cases and high/critical security findings block even when aggregate quality improves.

Baseline changes are classified as improvement, neutral, non-blocking regression, or blocking regression. The comparison includes prompt, model, embedding, retriever, agent/tool logic, quality, latency, throughput, and token usage where evidence exists.

Thresholds are examples, not universal production promises. Calibrate them with expert labels, production distributions, user harm, failure cost, evaluator reliability, model variance, and budget.

## RAG diagnosis matrix

| Context precision | Faithfulness | Interpretation |
|---:|---:|---|
| Low | High | Model used evidence faithfully, but retrieval included poor evidence |
| High | Low | Correct evidence was present; generation added unsupported claims |
| Low recall | Any | Needed evidence never arrived; inspect embedding, search, chunks, top-k, or KB |
| Good quality | Good, high latency | Inspect performance configuration and trace timing |
