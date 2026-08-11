from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Single secret-safe configuration surface for every adapter."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    azure_openai_api_key: SecretStr | None = None
    azure_openai_endpoint: str | None = None
    azure_openai_api_version: str = "2024-10-21"
    azure_openai_chat_deployment: str | None = None
    azure_openai_evaluator_deployment: str | None = None
    azure_openai_embedding_deployment: str | None = None
    azure_openai_model_a_deployment: str | None = None
    azure_openai_model_b_deployment: str | None = None

    observability_backend: Literal["none", "phoenix", "langfuse"] = "none"
    phoenix_endpoint: str = "http://localhost:6006"
    phoenix_api_key: SecretStr | None = None
    langfuse_public_key: str | None = None
    langfuse_secret_key: SecretStr | None = None
    langfuse_host: str = "http://localhost:3000"

    aiq_profile: Literal["dev", "pr", "nightly", "release"] = "dev"
    aiq_max_evaluation_cases: int = Field(default=10, ge=1, le=10_000)
    aiq_max_concurrency: int = Field(default=2, ge=1, le=100)
    aiq_evaluation_budget_usd: float = Field(default=5.0, ge=0)
    aiq_allow_live_model_calls: bool = False
    aiq_security_authorized: bool = False
    aiq_performance_authorized: bool = False
    aiq_random_seed: int = 42
    aiq_trace_content: bool = False

    @field_validator("azure_openai_endpoint")
    @classmethod
    def normalize_endpoint(cls, value: str | None) -> str | None:
        return value.rstrip("/") if value else None

    def require_azure(self, *, evaluator: bool = False, embeddings: bool = False) -> None:
        missing: list[str] = []
        for name in ("azure_openai_api_key", "azure_openai_endpoint"):
            if not getattr(self, name):
                missing.append(name.upper())
        deployment = (
            self.azure_openai_evaluator_deployment
            if evaluator
            else self.azure_openai_embedding_deployment
            if embeddings
            else self.azure_openai_chat_deployment
        )
        if not deployment:
            missing.append(
                "AZURE_OPENAI_EVALUATOR_DEPLOYMENT"
                if evaluator
                else "AZURE_OPENAI_EMBEDDING_DEPLOYMENT"
                if embeddings
                else "AZURE_OPENAI_CHAT_DEPLOYMENT"
            )
        if missing:
            raise RuntimeError(f"Missing required Azure OpenAI configuration: {', '.join(missing)}")
        if not self.aiq_allow_live_model_calls:
            raise RuntimeError(
                "Live model calls are disabled. Set AIQ_ALLOW_LIVE_MODEL_CALLS=true."
            )

    def safe_summary(self) -> dict[str, Any]:
        return {
            "profile": self.aiq_profile,
            "live_model_calls": self.aiq_allow_live_model_calls,
            "observability_backend": self.observability_backend,
            "azure_endpoint_configured": bool(self.azure_openai_endpoint),
            "chat_deployment": self.azure_openai_chat_deployment,
            "evaluator_deployment": self.azure_openai_evaluator_deployment,
            "embedding_deployment": self.azure_openai_embedding_deployment,
            "max_cases": self.aiq_max_evaluation_cases,
            "max_concurrency": self.aiq_max_concurrency,
            "budget_usd": self.aiq_evaluation_budget_usd,
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()


def load_yaml(path: str | Path) -> dict[str, Any]:
    resolved = Path(path)
    if not resolved.is_absolute():
        resolved = ROOT / resolved
    with resolved.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Expected a YAML mapping in {resolved}")
    return data
