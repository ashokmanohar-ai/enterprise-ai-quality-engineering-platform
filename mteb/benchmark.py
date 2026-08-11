from __future__ import annotations

import json
import os
from typing import Any

from ai_quality.config import ROOT, get_settings
from ai_quality.evaluation.contracts import EvaluationResult
from ai_quality.evaluation.embedding_runner import RetrievalExample, application_retrieval_benchmark
from ai_quality.models.embeddings import AzureEmbeddingProvider, SentenceTransformerEmbedding


class AzureMTEBEncoder:
    """Custom MTEB encoder adapter; Azure is not a model from MTEB's registry."""

    def __init__(self) -> None:
        self.provider = AzureEmbeddingProvider(get_settings())

    def encode(self, inputs: Any, **kwargs: Any) -> list[list[float]]:
        del kwargs
        if isinstance(inputs, list) and (not inputs or isinstance(inputs[0], str)):
            sentences = inputs
        else:
            sentences = [text for batch in inputs for text in batch]
        return self.provider.embed(sentences)


def _application_examples() -> list[RetrievalExample]:
    path = ROOT / "datasets" / "embeddings" / "retrieval-benchmark.jsonl"
    return [
        RetrievalExample(**json.loads(line))
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _write_normalized(results: list[EvaluationResult]) -> None:
    path = ROOT / "reports" / "normalized" / "nightly-embeddings.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(item.model_dump_json() + "\n" for item in results), encoding="utf-8")


def main() -> None:
    try:
        import mteb
    except ImportError as exc:
        raise RuntimeError("Install MTEB with: pip install -e '.[embeddings]'") from exc
    tasks = mteb.get_tasks(
        tasks=os.getenv("AIQ_MTEB_TASKS", "NFCorpus,SciFact").split(","), languages=["eng"]
    )
    output = ROOT / "reports" / "raw" / "mteb"
    output.mkdir(parents=True, exist_ok=True)
    candidates = {
        "azure-primary": AzureMTEBEncoder(),
        "local-baseline": mteb.get_model("sentence-transformers/all-MiniLM-L6-v2"),
    }
    summaries: dict[str, list[str]] = {}
    for name, candidate in candidates.items():
        cache = mteb.ResultCache(cache_path=str(output / name))
        native = mteb.evaluate(
            candidate, tasks=tasks, cache=cache, encode_kwargs={"batch_size": 16}
        )
        summaries[name] = [str(item) for item in native]
    (output / "run-summary.json").write_text(json.dumps(summaries, indent=2), encoding="utf-8")

    examples = _application_examples()
    normalized: list[EvaluationResult] = []
    normalized.extend(
        application_retrieval_benchmark(
            AzureEmbeddingProvider(get_settings()), examples, candidate="azure-primary"
        )
    )
    normalized.extend(
        application_retrieval_benchmark(
            SentenceTransformerEmbedding(), examples, candidate="local-baseline"
        )
    )
    normalized.append(
        EvaluationResult(
            test_id="suite:embeddings",
            framework="aiq",
            category="suite",
            metric="suite_completed",
            score=1.0,
            threshold=1.0,
            passed=True,
            metadata={"suite": "embeddings"},
        )
    )
    _write_normalized(normalized)


if __name__ == "__main__":
    main()
