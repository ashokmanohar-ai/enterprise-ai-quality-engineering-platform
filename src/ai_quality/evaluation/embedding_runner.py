from __future__ import annotations

from dataclasses import dataclass
from statistics import mean

from ai_quality.evaluation.contracts import EvaluationResult
from ai_quality.evaluation.thresholds import quality_threshold
from ai_quality.models.embeddings import EmbeddingProvider
from ai_quality.retrieval.vector_store import cosine


@dataclass(frozen=True)
class RetrievalExample:
    id: str
    query: str
    positive: str
    negatives: list[str]


def application_retrieval_benchmark(
    provider: EmbeddingProvider,
    examples: list[RetrievalExample],
    *,
    profile: str = "nightly",
    candidate: str = "candidate",
) -> list[EvaluationResult]:
    results: list[EvaluationResult] = []
    for example in examples:
        texts = [example.query, example.positive, *example.negatives]
        query, positive, *negatives = provider.embed(texts)
        positive_score = cosine(query, positive)
        negative_scores = [cosine(query, item) for item in negatives]
        rank_one = positive_score > max(negative_scores, default=-1.0)
        margin = max(0.0, min(1.0, (positive_score - max(negative_scores, default=-1.0) + 1) / 2))
        results.append(
            EvaluationResult(
                test_id=f"{candidate}:{example.id}",
                framework="custom",
                category="embeddings",
                metric="retrieval_rank_1",
                score=1.0 if rank_one else 0.0,
                threshold=1.0,
                passed=rank_one,
                reason=(
                    f"positive={positive_score:.4f}, "
                    f"max_negative={max(negative_scores, default=0):.4f}"
                ),
                metadata={"similarity_margin": margin, "candidate": candidate},
            )
        )
    if results:
        average = mean(item.score or 0.0 for item in results)
        threshold = quality_threshold("retrieval_rank_1", profile, 0.8)
        results.append(
            EvaluationResult(
                test_id=f"embedding-benchmark:{candidate}:aggregate",
                framework="custom",
                category="embeddings",
                metric="retrieval_rank_1",
                score=average,
                threshold=threshold,
                passed=average >= threshold,
                reason="Application-specific retrieval benchmark aggregate.",
                metadata={"candidate": candidate},
            )
        )
    return results
