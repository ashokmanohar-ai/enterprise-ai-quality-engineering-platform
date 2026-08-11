# Compatibility and upgrades

Verified 2026-08-11 against official project documentation, repositories, release pages, PyPI/npm records, and Microsoft Azure documentation.

## Key 2026 constraints

- PyRIT moved from the archived `Azure/PyRIT` notice repository to `microsoft/PyRIT`; stable package 1.0.1 uses executor-oriented attack APIs.
- Ragas 0.4 moved to collections metrics and experiment-centric evaluation; new adapters use `ascore`/`MetricResult` and avoid deprecated `evaluate()`.
- MCP Python SDK/Inspector v2 implement the 2026-07-28 protocol line. Python server examples use `MCPServer`, not the v1-only quickstart surface.
- MCP Python SDK 2.0 requires Pydantic 2.12 or newer. The shared core pins Pydantic 2.13.4 and pydantic-settings 2.15.0 so the MCP extra resolves cleanly.
- Promptfoo 0.122.0 dropped Node 20; use Node 24 in this repository.
- Garak 0.16 prefers `--spec`; older probe-tag/eval-threshold patterns are deprecated.
- AIPerf 0.12 is the successor path for GenAI-Perf-style benchmarking; TTFT/ITL require streaming.
- Phoenix and Langfuse are both OpenTelemetry-oriented. Select one production destination.
- Microsoft Foundry v1 removes dated `api-version` for supported v1 clients, but this cross-tool reference retains `AZURE_OPENAI_API_VERSION` because several integrations still expose versioned Azure chat endpoints. Review this when all selected tools support the v1 endpoint consistently.

## Upgrade procedure

1. Open an upgrade branch; never bump every tool blindly.
2. Read official release/migration/security notes for one tool and its transitive dependencies.
3. Update the matrix, pin, and native adapter together.
4. Run dataset contract tests and a no-network adapter smoke.
5. Run a small authorized live canary and inspect raw output shape.
6. Verify normalization preserves native score, unit, severity source, and reasons.
7. Run baseline/candidate on the same dataset and evaluator.
8. Review cost, telemetry/privacy, Python/Node, and container impact.
9. Merge only after the release gate and human tool-owner approval.

Package extras isolate heavy/security/performance toolchains. If a resolver conflict appears, keep native runners in dedicated lockfiles/containers and exchange only canonical inputs and normalized results.

## Official sources

- DeepEval: <https://deepeval.com/docs/>
- Ragas: <https://docs.ragas.io/en/stable/>
- Promptfoo: <https://www.promptfoo.dev/docs/>
- PyRIT: <https://github.com/microsoft/PyRIT>
- Garak: <https://docs.garak.ai/garak>
- MTEB: <https://github.com/embeddings-benchmark/mteb>
- MCP: <https://modelcontextprotocol.io/specification/2026-07-28>
- MCP Python: <https://py.sdk.modelcontextprotocol.io/>
- MCP Inspector: <https://modelcontextprotocol.io/docs/2026-07-28/tools/inspector>
- AIPerf: <https://docs.nvidia.com/aiperf/>
- Phoenix: <https://arize.com/docs/phoenix>
- Langfuse: <https://langfuse.com/docs>
- Azure OpenAI: <https://learn.microsoft.com/azure/ai-foundry/openai/>
