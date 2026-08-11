from __future__ import annotations

from typing import Any

from openai import AsyncAzureOpenAI

from ai_quality.config import Settings, get_settings
from ai_quality.evaluation.contracts import CanonicalCase, EvaluationResult
from ai_quality.evaluation.datasets import to_ragas
from ai_quality.evaluation.thresholds import quality_threshold


async def run_ragas_case(
    case: CanonicalCase,
    actual_output: str,
    retrieved_contexts: list[str],
    *,
    settings: Settings | None = None,
    profile: str = "pr",
) -> list[EvaluationResult]:
    """Ragas 0.4 collections API; avoids deprecated evaluate()/single_turn_ascore()."""
    try:
        from ragas.llms import llm_factory
        from ragas.metrics.collections import (
            ContextPrecision,
            ContextRecall,
            FactualCorrectness,
            Faithfulness,
            NoiseSensitivity,
            ResponseRelevancy,
        )
    except ImportError as exc:
        raise RuntimeError("Install Ragas with: pip install -e '.[rag]'") from exc
    configured = settings or get_settings()
    configured.require_azure(evaluator=True)
    assert configured.azure_openai_api_key is not None
    assert configured.azure_openai_endpoint is not None
    assert configured.azure_openai_evaluator_deployment is not None
    client = AsyncAzureOpenAI(
        api_key=configured.azure_openai_api_key.get_secret_value(),
        api_version=configured.azure_openai_api_version,
        azure_endpoint=configured.azure_openai_endpoint,
    )
    llm = llm_factory(configured.azure_openai_evaluator_deployment, client=client)
    metrics: list[Any] = [
        Faithfulness(llm=llm),
        ContextPrecision(llm=llm),
        ContextRecall(llm=llm),
        FactualCorrectness(llm=llm),
        NoiseSensitivity(llm=llm),
        ResponseRelevancy(llm=llm),
    ]
    payload = to_ragas(case, actual_output, retrieved_contexts)
    results: list[EvaluationResult] = []
    for metric in metrics:
        native = await metric.ascore(**payload)
        score = float(native.value)
        name = {
            "Faithfulness": "faithfulness",
            "ContextPrecision": "context_precision",
            "ContextRecall": "context_recall",
            "FactualCorrectness": "answer_correctness",
            "NoiseSensitivity": "noise_sensitivity",
            "ResponseRelevancy": "answer_relevance",
        }.get(metric.__class__.__name__, metric.name.lower().replace(" ", "_"))
        threshold = quality_threshold(name, profile, 0.75)
        results.append(
            EvaluationResult(
                test_id=case.id,
                framework="ragas",
                category="rag",
                metric=name,
                score=score,
                threshold=threshold,
                passed=score >= threshold,
                reason=native.reason or "",
                metadata={
                    "ragas_result": native.model_dump()
                    if hasattr(native, "model_dump")
                    else str(native)
                },
            )
        )
    return results
