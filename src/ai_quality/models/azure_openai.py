from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Any

from openai import AzureOpenAI

from ai_quality.config import Settings, get_settings


@dataclass(frozen=True)
class ModelResponse:
    text: str
    latency_ms: float
    model: str
    token_usage: dict[str, int]
    raw_id: str | None = None


class AzureOpenAIModel:
    """Shared Azure OpenAI adapter used by applications and evaluators."""

    def __init__(self, deployment: str | None = None, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.settings.require_azure()
        self.deployment = deployment or self.settings.azure_openai_chat_deployment
        assert self.deployment is not None
        assert self.settings.azure_openai_api_key is not None
        assert self.settings.azure_openai_endpoint is not None
        self.client = AzureOpenAI(
            api_key=self.settings.azure_openai_api_key.get_secret_value(),
            api_version=self.settings.azure_openai_api_version,
            azure_endpoint=self.settings.azure_openai_endpoint,
        )

    def complete(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float = 0,
        max_output_tokens: int = 800,
        response_format: dict[str, Any] | None = None,
    ) -> ModelResponse:
        started = perf_counter()
        kwargs: dict[str, Any] = {
            "model": self.deployment,
            "messages": messages,
            "temperature": temperature,
            "max_completion_tokens": max_output_tokens,
        }
        if response_format:
            kwargs["response_format"] = response_format
        response = self.client.chat.completions.create(**kwargs)
        usage = response.usage
        return ModelResponse(
            text=response.choices[0].message.content or "",
            latency_ms=(perf_counter() - started) * 1000,
            model=self.deployment,
            token_usage={
                "input": usage.prompt_tokens if usage else 0,
                "output": usage.completion_tokens if usage else 0,
                "total": usage.total_tokens if usage else 0,
            },
            raw_id=response.id,
        )
