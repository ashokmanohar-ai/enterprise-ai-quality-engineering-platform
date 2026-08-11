from __future__ import annotations

from collections.abc import Callable
from typing import Any

from ai_quality.config import Settings, get_settings
from ai_quality.evaluation.contracts import CanonicalCase
from ai_quality.experiments.metadata import build_metadata


class PhoenixExperimentRunner:
    """Thin adapter over the Phoenix 3.x dataset and experiment client resources."""

    def __init__(self, settings: Settings | None = None) -> None:
        configured = settings or get_settings()
        try:
            from phoenix.client import Client
        except ImportError as exc:
            raise RuntimeError("Install Phoenix with: pip install -e '.[phoenix]'") from exc
        self.client = Client(
            base_url=configured.phoenix_endpoint,
            api_key=configured.phoenix_api_key.get_secret_value()
            if configured.phoenix_api_key
            else None,
        )
        self.metadata = build_metadata(configured)

    def upload_dataset(self, name: str, cases: list[CanonicalCase]):  # type: ignore[no-untyped-def]
        return self.client.datasets.create_dataset(
            name=name,
            dataset_description="Sanitized AcmeCloud canonical AI Quality Engineering cases.",
            inputs=[
                {"test_case_id": case.id, "question": case.input, "contexts": case.contexts}
                for case in cases
            ],
            outputs=[{"reference_answer": case.reference_answer} for case in cases],
            metadata=[
                {
                    "tags": case.tags,
                    "critical": case.critical,
                    "git_commit": self.metadata.git_commit,
                    "dataset_version": self.metadata.dataset_version,
                    "prompt_version": self.metadata.prompt_version,
                }
                for case in cases
            ],
        )

    def run(
        self,
        *,
        dataset: Any,
        task: Callable[[Any], Any],
        evaluators: list[Any],
    ):  # type: ignore[no-untyped-def]
        return self.client.experiments.run_experiment(
            dataset=dataset,
            task=task,
            evaluators=evaluators,
        )
