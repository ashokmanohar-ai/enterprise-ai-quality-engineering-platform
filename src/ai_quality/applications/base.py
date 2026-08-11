from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, Protocol

from ai_quality.applications.agent_app import DeterministicSupportAgent
from ai_quality.applications.llm_app import CustomerSupportLLM
from ai_quality.applications.mcp_agent import MCPEnabledSupportAgent
from ai_quality.applications.rag_app import PolicyRAGAssistant


@dataclass(frozen=True)
class AUTRequest:
    input: str
    contexts: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AUTResponse:
    output: str
    contexts: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    latency_ms: float | None = None
    token_usage: dict[str, int] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


class ApplicationUnderTest(Protocol):
    async def invoke(self, request: AUTRequest) -> AUTResponse: ...


class CustomerSupportAUT:
    def __init__(self, application: CustomerSupportLLM | None = None) -> None:
        self.application = application or CustomerSupportLLM()

    async def invoke(self, request: AUTRequest) -> AUTResponse:
        result = await asyncio.to_thread(self.application.answer, request.input, request.contexts)
        return AUTResponse(
            output=result.answer,
            contexts=request.contexts,
            latency_ms=result.latency_ms,
            token_usage=result.token_usage,
            metadata={"model": result.model},
        )


class RAGAssistantAUT:
    def __init__(self, application: PolicyRAGAssistant | None = None) -> None:
        self.application = application or PolicyRAGAssistant()

    async def invoke(self, request: AUTRequest) -> AUTResponse:
        result = await asyncio.to_thread(self.application.answer, request.input)
        return AUTResponse(
            output=result.answer,
            contexts=result.contexts,
            sources=result.sources,
            latency_ms=result.generation.latency_ms,
            token_usage=result.generation.token_usage,
            metadata={"retrieval_scores": result.retrieval_scores},
        )


class SupportAgentAUT:
    def __init__(self, application: DeterministicSupportAgent | None = None) -> None:
        self.application = application or DeterministicSupportAgent()

    async def invoke(self, request: AUTRequest) -> AUTResponse:
        result = await asyncio.to_thread(
            self.application.run,
            request.input,
            requester_account_id=str(request.metadata.get("requester_account_id", "acct-100")),
            confirmed=bool(request.metadata.get("confirmed", False)),
        )
        return _agent_response(result)


class MCPSupportAgentAUT:
    def __init__(self, application: MCPEnabledSupportAgent | None = None) -> None:
        self.application = application or MCPEnabledSupportAgent()

    async def invoke(self, request: AUTRequest) -> AUTResponse:
        result = await self.application.run(
            request.input,
            requester_account_id=str(request.metadata.get("requester_account_id", "acct-100")),
            confirmed=bool(request.metadata.get("confirmed", False)),
        )
        return _agent_response(result)


def _agent_response(result) -> AUTResponse:  # type: ignore[no-untyped-def]
    return AUTResponse(
        output=result.final_answer,
        tool_calls=[
            {"name": call.name, "arguments": call.arguments, "result": call.result}
            for call in result.tool_calls
        ],
        metadata={"completed": result.completed, "blocked_reason": result.blocked_reason},
    )
