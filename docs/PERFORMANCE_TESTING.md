# Performance testing with AIPerf

AIPerf 0.12.0 measures a live OpenAI-compatible endpoint. It does not simulate model capacity. The wrapper uses `aiperf profile`, `--endpoint-type chat`, canonical input, concurrency, request count, warmup, and streaming.

Native metric names retained in metadata include request latency, time to first token, inter-token latency, output token throughput, request throughput, and error rate. Streaming is required for TTFT and ITL.

Profiles:

- smoke: one concurrent user, five requests;
- load: expected reference concurrency;
- stress: controlled ramp beyond expected load;
- soak: one-hour reference duration, run only in an approved window.

Thresholds are configured, never embedded in runner code. Normalize P95 request latency/TTFT/ITL, throughput, and error rate, preserving native metric/unit. Compare baseline and candidate under the same region, deployment capacity, prompt distribution, output lengths, warmup, concurrency, and time window.

Azure compatibility must be tested in the target environment. If the endpoint/header shape is not accepted by AIPerf's native chat endpoint, use its documented template endpoint plugin. Do not invent flags or patch AIPerf internals.

Set `AIQ_PERFORMANCE_AUTHORIZED=true` only with target-owner approval. Never run stress or soak against shared production without capacity/incident approval.
