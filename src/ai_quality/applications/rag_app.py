from __future__ import annotations

from dataclasses import dataclass

from ai_quality.applications.llm_app import AppAnswer, CustomerSupportLLM
from ai_quality.observability.telemetry import content_attributes, get_backend
from ai_quality.retrieval.retriever import PolicyRetriever


@dataclass(frozen=True)
class RAGAnswer:
    answer: str
    contexts: list[str]
    sources: list[str]
    retrieval_scores: list[float]
    generation: AppAnswer


class PolicyRAGAssistant:
    def __init__(
        self,
        retriever: PolicyRetriever | None = None,
        llm: CustomerSupportLLM | None = None,
        backend=None,
    ) -> None:  # type: ignore[no-untyped-def]
        self.backend = backend or get_backend()
        self.retriever = retriever or PolicyRetriever()
        self.llm = llm or CustomerSupportLLM(backend=self.backend)

    def answer(self, question: str) -> RAGAnswer:
        with self.backend.span("rag_request", attributes=content_attributes("input", question)):
            with self.backend.span("query_processing", attributes={"query.length": len(question)}):
                query = question.strip()
            with self.backend.span(
                "retrieval", attributes={"retriever.top_k": self.retriever.top_k}
            ):
                hits = self.retriever.retrieve(query)
                contexts = [hit.text for hit in hits]
            with self.backend.span(
                "prompt_construction", attributes={"context.count": len(contexts)}
            ):
                sources = [hit.metadata["source"] for hit in hits]
            with self.backend.span("generation", attributes={"source.count": len(sources)}):
                generation = self.llm.answer(question, contexts)
            return RAGAnswer(
                answer=generation.answer,
                contexts=contexts,
                sources=sources,
                retrieval_scores=[hit.score for hit in hits],
                generation=generation,
            )
