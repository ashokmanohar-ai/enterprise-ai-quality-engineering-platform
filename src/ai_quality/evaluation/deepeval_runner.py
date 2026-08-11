from __future__ import annotations

import asyncio
from typing import Any, TypeVar

from pydantic import BaseModel

from ai_quality.config import Settings, get_settings
from ai_quality.evaluation.contracts import CanonicalCase, EvaluationResult
from ai_quality.evaluation.datasets import to_deepeval
from ai_quality.evaluation.thresholds import quality_threshold
from ai_quality.models.azure_openai import AzureOpenAIModel

SchemaT = TypeVar("SchemaT", bound=BaseModel)


class AzureDeepEvalJudge:
    """Factory for DeepEval's documented custom-model interface."""

    @staticmethod
    def build(settings: Settings | None = None):  # type: ignore[no-untyped-def]
        try:
            from deepeval.models import DeepEvalBaseLLM
        except ImportError as exc:
            raise RuntimeError("Install DeepEval with: pip install -e '.[llm]'") from exc
        configured = settings or get_settings()
        configured.require_azure(evaluator=True)
        deployment = configured.azure_openai_evaluator_deployment

        class Judge(DeepEvalBaseLLM):  # type: ignore[misc,valid-type]
            def load_model(self):  # type: ignore[no-untyped-def]
                return AzureOpenAIModel(deployment=deployment, settings=configured)

            def generate(self, prompt: str, schema: type[SchemaT] | None = None) -> str | SchemaT:
                response = (
                    self.load_model()
                    .complete(
                        [{"role": "user", "content": prompt}],
                        max_output_tokens=1600,
                        response_format={"type": "json_object"} if schema else None,
                    )
                    .text
                )
                return schema.model_validate_json(response) if schema else response

            async def a_generate(
                self, prompt: str, schema: type[SchemaT] | None = None
            ) -> str | SchemaT:
                return await asyncio.to_thread(self.generate, prompt, schema)

            def get_model_name(self) -> str:
                return f"azure:{deployment}"

        return Judge()


def run_deepeval_case(
    case: CanonicalCase,
    actual_output: str,
    *,
    settings: Settings | None = None,
    profile: str = "pr",
) -> list[EvaluationResult]:
    try:
        from deepeval.metrics import (
            AnswerRelevancyMetric,
            FaithfulnessMetric,
            GEval,
            HallucinationMetric,
        )
        from deepeval.test_case import LLMTestCase, LLMTestCaseParams
    except ImportError as exc:
        raise RuntimeError("Install DeepEval with: pip install -e '.[llm]'") from exc
    judge = AzureDeepEvalJudge.build(settings)
    payload = to_deepeval(case, actual_output)
    test_case = LLMTestCase(**payload)
    relevance_threshold = quality_threshold("answer_relevance", profile, 0.8)
    faithfulness_threshold = quality_threshold("faithfulness", profile, 0.8)
    metrics: list[Any] = [
        AnswerRelevancyMetric(threshold=relevance_threshold, model=judge, include_reason=True),
        GEval(
            name="Professional quality",
            criteria=(
                "The answer is concise, professional, follows business rules, "
                "and directly answers the request."
            ),
            evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
            threshold=quality_threshold("professional_quality", profile, 0.8),
            model=judge,
        ),
    ]
    if case.contexts:
        metrics.extend(
            [
                FaithfulnessMetric(
                    threshold=faithfulness_threshold, model=judge, include_reason=True
                ),
                HallucinationMetric(
                    threshold=1.0 - quality_threshold("groundedness", profile, 0.8),
                    model=judge,
                    include_reason=True,
                ),
            ]
        )
    normalized: list[EvaluationResult] = []
    for metric in metrics:
        metric.measure(test_case)
        raw_score = float(metric.score)
        higher_is_better = metric.__class__.__name__ != "HallucinationMetric"
        normalized_score = raw_score if higher_is_better else 1.0 - raw_score
        native_threshold = float(getattr(metric, "threshold", 0.8))
        normalized_threshold = native_threshold if higher_is_better else 1.0 - native_threshold
        canonical_name = {
            "AnswerRelevancyMetric": "answer_relevance",
            "FaithfulnessMetric": "faithfulness",
            "HallucinationMetric": "groundedness",
            "GEval": "professional_quality",
        }.get(metric.__class__.__name__, str(metric.name).lower().replace(" ", "_"))
        normalized.append(
            EvaluationResult(
                test_id=case.id,
                framework="deepeval",
                category="llm",
                metric=canonical_name,
                score=normalized_score,
                threshold=normalized_threshold,
                passed=bool(metric.is_successful()),
                reason=str(getattr(metric, "reason", "")),
                metadata={
                    "native_score": raw_score,
                    "native_threshold": native_threshold,
                    "native_metric": metric.__class__.__name__,
                },
            )
        )
    return normalized
