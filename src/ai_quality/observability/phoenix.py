from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from ai_quality.config import Settings


class PhoenixBackend:
    """Primary backend using Phoenix/OpenInference OpenTelemetry export."""

    def __init__(self, settings: Settings) -> None:
        try:
            from phoenix.client import Client
            from phoenix.otel import register
        except ImportError as exc:
            raise RuntimeError("Install Phoenix extras with: pip install -e '.[phoenix]'") from exc
        headers: dict[str, str] = {}
        if settings.phoenix_api_key:
            headers["api_key"] = settings.phoenix_api_key.get_secret_value()
        self.tracer_provider = register(endpoint=settings.phoenix_endpoint, headers=headers)
        self.tracer = self.tracer_provider.get_tracer("enterprise-ai-quality")
        self.client = Client(
            base_url=settings.phoenix_endpoint,
            api_key=settings.phoenix_api_key.get_secret_value()
            if settings.phoenix_api_key
            else None,
        )

    @contextmanager
    def span(self, name: str, *, attributes: dict[str, Any]) -> Iterator[Any]:
        with self.tracer.start_as_current_span(name, attributes=attributes) as span:
            yield span

    def score(
        self, *, trace_id: str, name: str, value: float, metadata: dict[str, Any] | None = None
    ) -> None:
        details = dict(metadata or {})
        span_id = str(details.pop("span_id", trace_id))
        self.client.spans.add_span_annotation(
            span_id=span_id,
            annotation_name=name,
            annotator_kind="CODE",
            score=value,
            metadata=details,
        )

    def flush(self) -> None:
        self.tracer_provider.force_flush()
