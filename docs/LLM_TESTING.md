# LLM testing with DeepEval

DeepEval owns model-mediated unit tests and judge-based response quality. Deterministic assertions should check exact business rules first; an LLM judge should evaluate qualities that cannot be expressed reliably as code.

The runner uses DeepEval 4.0.3 with a custom `DeepEvalBaseLLM` backed by the shared Azure evaluator deployment. It constructs `LLMTestCase` inputs and normalizes:

- Answer Relevancy;
- Faithfulness when context exists;
- Hallucination, inverted to higher-is-better while preserving the native score;
- G-Eval professional/business quality;
- agent task/tool/argument/efficiency metrics as an extension for live traced agents.

Run:

```bash
pip install -e '.[llm]'
AIQ_ALLOW_LIVE_MODEL_CALLS=true make test-llm
```

DeepEval integrates with pytest, but tests skip locally while live calls are disabled. CI enables live calls through protected settings. Keep temperature zero, separate application/evaluator deployments, and align judge output to expert labels before treating it as release evidence.

Judge failure, provider timeout, malformed structured judge output, or missing suite evidence is not a pass. Store score, reason, model, token use, latency, and trace ID in the normalized contract.
