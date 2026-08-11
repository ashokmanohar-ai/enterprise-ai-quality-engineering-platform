import pytest

from ai_quality.applications.rag_app import PolicyRAGAssistant
from ai_quality.config import get_settings
from ai_quality.evaluation.datasets import load_jsonl
from ai_quality.evaluation.ragas_runner import run_ragas_case


@pytest.mark.rag
@pytest.mark.asyncio
async def test_rag_case_with_ragas() -> None:
    settings = get_settings()
    if not settings.aiq_allow_live_model_calls:
        pytest.skip("Live model calls disabled")
    case = next(
        item for item in load_jsonl("datasets/golden/golden.jsonl") if item.category == "rag"
    )
    answer = PolicyRAGAssistant().answer(case.input)
    results = await run_ragas_case(case, answer.answer, answer.contexts, settings=settings)
    assert results
