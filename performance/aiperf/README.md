# AIPerf 0.12

The wrapper uses the native `aiperf profile` command with an OpenAI-compatible chat endpoint, streaming, a canonical input file, explicit concurrency/request count, and warmup. Streaming is mandatory for TTFT and ITL. Azure endpoint/header compatibility must be validated in the target environment; if the deployment cannot accept AIPerf's native OpenAI-compatible request shape, use AIPerf's documented template endpoint plugin instead of modifying AIPerf internals.
