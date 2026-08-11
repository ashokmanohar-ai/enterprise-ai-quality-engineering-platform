# Prompt regression and model comparison

Promptfoo owns prompt versions, Azure deployment comparison, assertion-driven checks, structured output checks, LLM rubrics, and repeatable application-specific security regressions.

Configs:

- `regression.yaml`: customer-support v1 versus v2;
- `model-comparison.yaml`: Azure deployment A versus B;
- `redteam.yaml`: authorized security smoke;
- `promptfooconfig.yaml`: default suite.

Promptfoo 0.122.0 uses `azure:chat:<deployment>` and the shared environment values. Node.js 24 is required by this repository because 0.122.0 dropped Node 20.

```bash
npm ci
npm run prompt:test
npm run prompt:compare
```

Use identical generated tests for every prompt/model cell. Compare case-level failures, not only aggregate score. A single critical refund, deletion, authorization, or security regression blocks. Clear Promptfoo cache for release comparisons unless cached output reuse is explicitly valid and identified in run metadata.
