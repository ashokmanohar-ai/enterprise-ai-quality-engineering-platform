from __future__ import annotations

from contextlib import AbstractContextManager
from typing import Any, Protocol


class Span(Protocol):
    def set_attribute(self, key: str, value: Any) -> None: ...
    def set_output(self, output: Any) -> None: ...


class ObservabilityBackend(Protocol):
    def span(self, name: str, *, attributes: dict[str, Any]) -> AbstractContextManager[Any]: ...
    def score(
        self, *, trace_id: str, name: str, value: float, metadata: dict[str, Any] | None = None
    ) -> None: ...
    def flush(self) -> None: ...
