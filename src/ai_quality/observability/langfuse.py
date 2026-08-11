from __future__ import annotations

import json
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from ai_quality.config import Settings


class LangfuseBackend:
    """Optional backend. Production telemetry is sent here only when selected."""

    def __init__(self, settings: Settings) -> None:
        try:
            from langfuse import Langfuse
        except ImportError as exc:
            raise RuntimeError(
                "Install Langfuse extras with: pip install -e '.[langfuse]'"
            ) from exc
        if not settings.langfuse_public_key or not settings.langfuse_secret_key:
            raise RuntimeError("LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY are required.")
        self.client = Langfuse(
            public_key=settings.langfuse_public_key,
            secret_key=settings.langfuse_secret_key.get_secret_value(),
            base_url=settings.langfuse_host,
        )

    @contextmanager
    def span(self, name: str, *, attributes: dict[str, Any]) -> Iterator[Any]:
        with self.client.start_as_current_observation(
            as_type="span", name=name, metadata=attributes
        ) as span:
            yield span

    def score(
        self, *, trace_id: str, name: str, value: float, metadata: dict[str, Any] | None = None
    ) -> None:
        comment = json.dumps(metadata, sort_keys=True)[:500] if metadata else None
        self.client.create_score(
            trace_id=trace_id,
            name=name,
            value=float(value),
            data_type="NUMERIC",
            comment=comment,
        )

    def flush(self) -> None:
        self.client.flush()
