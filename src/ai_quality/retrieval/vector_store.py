from __future__ import annotations

from dataclasses import dataclass
from math import sqrt

from ai_quality.models.embeddings import EmbeddingProvider


@dataclass(frozen=True)
class SearchHit:
    document_id: str
    text: str
    score: float
    metadata: dict[str, str]


def cosine(left: list[float], right: list[float]) -> float:
    numerator = sum(a * b for a, b in zip(left, right, strict=True))
    denominator = sqrt(sum(a * a for a in left)) * sqrt(sum(b * b for b in right))
    return numerator / denominator if denominator else 0.0


class InMemoryVectorStore:
    """Small reference store so every framework evaluates the same retriever."""

    def __init__(self, embeddings: EmbeddingProvider) -> None:
        self.embeddings = embeddings
        self._documents: list[tuple[str, str, dict[str, str], list[float]]] = []

    def add(self, documents: list[tuple[str, str, dict[str, str]]]) -> None:
        vectors = self.embeddings.embed([document[1] for document in documents])
        self._documents.extend(
            (document_id, text, metadata, vector)
            for (document_id, text, metadata), vector in zip(documents, vectors, strict=True)
        )

    def search(self, query: str, *, top_k: int = 3) -> list[SearchHit]:
        query_vector = self.embeddings.embed([query])[0]
        hits = [
            SearchHit(document_id, text, cosine(query_vector, vector), metadata)
            for document_id, text, metadata, vector in self._documents
        ]
        return sorted(hits, key=lambda item: item.score, reverse=True)[:top_k]
