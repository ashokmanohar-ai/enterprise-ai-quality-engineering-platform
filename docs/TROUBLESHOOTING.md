# Troubleshooting

## Bad production answer

Find trace → inspect retrieved chunks/ranks → inspect constructed prompt/version → inspect model/deployment/parameters → inspect agent tools and results → review evaluation scores → identify layer → sanitize into golden case → reproduce → fix → experiment → gate.

## RAG patterns

- Low context precision + high faithfulness: irrelevant retrieval, grounded generation. Inspect query, embedding, chunking, top-k, reranking.
- High context precision + low faithfulness: good evidence, unsupported answer. Inspect prompt/model/decoding.
- Low context recall: evidence never retrieved. Inspect KB ingestion, search, embedding, filters, chunks, top-k.
- Good RAG + high latency: inspect retrieval network/vector timing, prompt size, model TTFT/ITL, retries.

## Agent patterns

Wrong selection → tool descriptions/planner. Bad arguments → schema/argument extraction. Repeats/loops → stopping policy and state. Timeout → downstream tool and retry budget. Ignored correct result → synthesis prompt. Contradictory final → tool-result grounding. Unauthorized call → policy enforcement at tool boundary. Hallucinated tool → advertised tool list and model guard.

## MCP patterns

Unavailable server → command/cwd/transport/stderr. Invalid schema → `type: object`, annotations, required fields. Invalid arguments → protocol validation and readable tool error. Business violation → enforce inside tool, not only agent prompt. Misinterpreted result → structured content and agent test.

## Security and performance

Treat scanner hits as hypotheses until reproduced and reviewed. Preserve native probe/detector/scorer evidence. Never lower severity simply because a judge disagrees.

For performance, compare environment and load shape before blaming the model. Correlate slow AIPerf records to traces; isolate queuing, retrieval, prompt length, TTFT, token generation, tool latency, retry, and error paths.

## Reference failure scenarios

| Scenario | Evidence | Diagnosis and decision |
|---|---|---|
| Hallucinated policy | DeepEval/Ragas faithfulness fail; trace shows correct evidence | Generation problem; fix prompt/model and retain the case |
| Bad retriever | Low Ragas precision/recall; trace shows irrelevant or missing chunks | Retrieval problem; inspect embedding, chunking, filters, and top-k |
| Prompt regression | Promptfoo shows v2 loses cases passed by v1 | Case-level blocking regression; block the PR |
| Security vulnerability | Garak discovers; PyRIT reproduces; human confirms | Fix, sanitize, and add a permanent Promptfoo regression |
| Slow new model | Quality improves but AIPerf P95/TTFT violates the configured SLO | Reject or capacity-optimize despite the quality gain |
| Weak embedding upgrade | MTEB is competitive but application context recall drops | Reject it for this application; benchmark strength is not production fitness |
