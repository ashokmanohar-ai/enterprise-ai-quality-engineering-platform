from __future__ import annotations

from ai_quality.models.embeddings import DeterministicHashEmbedding, EmbeddingProvider
from ai_quality.retrieval.knowledge_base import load_policy_documents
from ai_quality.retrieval.vector_store import InMemoryVectorStore, SearchHit


class PolicyRetriever:
    def __init__(self, embeddings: EmbeddingProvider | None = None, *, top_k: int = 3) -> None:
        self.top_k = top_k
        self.store = InMemoryVectorStore(embeddings or DeterministicHashEmbedding())
        self.store.add(load_policy_documents())

    def retrieve(self, query: str) -> list[SearchHit]:
        return self.store.search(query, top_k=self.top_k)
