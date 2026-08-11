from __future__ import annotations

import hashlib
import math
from typing import Protocol

from openai import AzureOpenAI

from ai_quality.config import Settings, get_settings


class EmbeddingProvider(Protocol):
    def embed(self, texts: list[str]) -> list[list[float]]: ...


class AzureEmbeddingProvider:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.settings.require_azure(embeddings=True)
        assert self.settings.azure_openai_api_key is not None
        assert self.settings.azure_openai_endpoint is not None
        assert self.settings.azure_openai_embedding_deployment is not None
        self.client = AzureOpenAI(
            api_key=self.settings.azure_openai_api_key.get_secret_value(),
            api_version=self.settings.azure_openai_api_version,
            azure_endpoint=self.settings.azure_openai_endpoint,
        )

    def embed(self, texts: list[str]) -> list[list[float]]:
        response = self.client.embeddings.create(
            model=self.settings.azure_openai_embedding_deployment,
            input=texts,
        )
        return [item.embedding for item in response.data]


class SentenceTransformerEmbedding:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> None:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise RuntimeError(
                "Install embedding dependencies with: pip install -e '.[embeddings]'"
            ) from exc
        self.model = SentenceTransformer(model_name)

    def embed(self, texts: list[str]) -> list[list[float]]:
        return self.model.encode(texts, normalize_embeddings=True).tolist()


class DeterministicHashEmbedding:
    """Offline test double; not a production embedding model or an MTEB replacement."""

    def __init__(self, dimensions: int = 128) -> None:
        self.dimensions = dimensions

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._one(text) for text in texts]

    def _one(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        for token in text.lower().split():
            digest = hashlib.sha256(token.encode()).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimensions
            vector[index] += 1.0 if digest[4] % 2 else -1.0
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]
