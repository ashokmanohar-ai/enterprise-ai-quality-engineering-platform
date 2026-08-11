from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from ai_quality.config import Settings, get_settings
from ai_quality.models.azure_openai import AzureOpenAIModel
from ai_quality.models.embeddings import AzureEmbeddingProvider, EmbeddingProvider

ModelRole = Literal["application", "evaluator", "candidate_a", "candidate_b"]


@dataclass(frozen=True)
class ModelRegistry:
    """The one deployment-resolution point used by applications and evaluators."""

    settings: Settings

    @classmethod
    def from_environment(cls) -> ModelRegistry:
        return cls(get_settings())

    def chat(self, role: ModelRole = "application") -> AzureOpenAIModel:
        deployments = {
            "application": self.settings.azure_openai_chat_deployment,
            "evaluator": self.settings.azure_openai_evaluator_deployment,
            "candidate_a": self.settings.azure_openai_model_a_deployment,
            "candidate_b": self.settings.azure_openai_model_b_deployment,
        }
        deployment = deployments[role]
        if not deployment:
            raise RuntimeError(f"Azure deployment for role '{role}' is not configured")
        return AzureOpenAIModel(deployment=deployment, settings=self.settings)

    def embeddings(self) -> EmbeddingProvider:
        return AzureEmbeddingProvider(settings=self.settings)
