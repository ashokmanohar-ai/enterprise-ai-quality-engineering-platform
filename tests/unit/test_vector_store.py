from ai_quality.models.embeddings import DeterministicHashEmbedding
from ai_quality.retrieval.vector_store import InMemoryVectorStore, cosine


def test_cosine_identity() -> None:
    assert cosine([1.0, 0.0], [1.0, 0.0]) == 1.0


def test_store_returns_ranked_hits() -> None:
    store = InMemoryVectorStore(DeterministicHashEmbedding())
    store.add(
        [
            ("refund", "refund within thirty days", {"source": "refund"}),
            ("shipping", "shipping security key", {"source": "shipping"}),
        ]
    )
    hits = store.search("refund thirty days", top_k=1)
    assert hits[0].document_id == "refund"
