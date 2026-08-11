from __future__ import annotations

import hashlib
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from ai_quality.config import Settings, get_settings


def content_attributes(name: str, value: str, settings: Settings | None = None) -> dict[str, Any]:
    configured = settings or get_settings()
    attributes: dict[str, Any] = {
        f"{name}.length": len(value),
        f"{name}.sha256": hashlib.sha256(value.encode()).hexdigest(),
    }
    if configured.aiq_trace_content:
        attributes[name] = value
    return attributes


class NoOpBackend:
    @contextmanager
    def span(self, name: str, *, attributes: dict[str, Any]) -> Iterator[None]:
        del name, attributes
        yield None

    def score(
        self, *, trace_id: str, name: str, value: float, metadata: dict[str, Any] | None = None
    ) -> None:
        del trace_id, name, value, metadata

    def flush(self) -> None:
        return None


def get_backend(settings: Settings | None = None):  # type: ignore[no-untyped-def]
    configured = settings or get_settings()
    if configured.observability_backend == "phoenix":
        from ai_quality.observability.phoenix import PhoenixBackend

        return PhoenixBackend(configured)
    if configured.observability_backend == "langfuse":
        from ai_quality.observability.langfuse import LangfuseBackend

        return LangfuseBackend(configured)
    return NoOpBackend()
