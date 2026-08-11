# RAG testing with Ragas

Ragas owns detailed retrieval/generation diagnosis. The implementation targets Ragas 0.4.3 collections metrics and `ascore(**kwargs)`, which returns a structured `MetricResult`. It intentionally avoids deprecated `evaluate()` and legacy `single_turn_ascore()` examples.

Core metrics:

- `Faithfulness`: generated claims supported by retrieved contexts;
- `ResponseRelevancy`: response alignment to user input;
- `ContextPrecision`: relevant chunks ranked early;
- `ContextRecall`: required reference evidence retrieved;
- `FactualCorrectness`: response versus reference;
- `NoiseSensitivity`: robustness to irrelevant context.

Run retriever-only tests first, then generation, then end-to-end. A retrieval failure means relevant evidence is missing or badly ranked. A generation failure means correct evidence arrived but the answer ignored, contradicted, or exceeded it.

```bash
pip install -e '.[rag]'
AIQ_ALLOW_LIVE_MODEL_CALLS=true make test-rag
```

Record top-k, chunking, embedding deployment, corpus version, reranking, prompt, and model in each experiment. Compare top-k 3 versus 8 with the same cases; do not compare runs with silently different corpora.
