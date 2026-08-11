# Observability and experiments

Phoenix is primary; Langfuse is an optional adapter. `OBSERVABILITY_BACKEND` selects one. Duplicate telemetry is disabled by architecture because it increases cost, privacy surface, and inconsistent trace identity.

Capture input/prompt, prompt version, model/deployment, output, token usage, latency, status/error, contexts/sources, tool calls/results, and run metadata. Apply content redaction and sampling appropriate to the environment.

RAG span hierarchy: request → query processing → retrieval → prompt construction → generation. Agent hierarchy: request → planning → tool calls/results → final generation.

Attach offline scores to the trace/experiment using `evaluation_run_id`, `experiment_id`, `test_case_id`, and `git_commit`. Phoenix provides OpenTelemetry/OpenInference tracing plus datasets, evaluations, and experiments. Langfuse v4 provides OpenTelemetry-based observations, scores, datasets, experiments, and prompt management.

Run experiments for prompt v1/v2, model A/B, embedding A/B, top-k 3/8, and agent strategy A/B. Hold dataset and evaluator constant. Store branch, commit, dataset hash, prompt version, deployments, retriever settings, timestamp, environment, seed, and tool versions.

Do not evaluate every production request with multiple judge models. Use deterministic online checks, sampling, human feedback, and offline replay to manage cost and privacy.
