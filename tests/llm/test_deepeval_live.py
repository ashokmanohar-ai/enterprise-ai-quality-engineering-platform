import pytest

from ai_quality.applications.llm_app import CustomerSupportLLM
from ai_quality.config import get_settings
from ai_quality.evaluation.datasets import load_jsonl
from ai_quality.evaluation.deepeval_runner import run_deepeval_case
from ai_quality.models.azure_openai import AzureOpenAIModel


@pytest.mark.llm
def test_refund_answer_with_deepeval() -> None:
    settings = get_settings()
    if not settings.aiq_allow_live_model_calls:
        pytest.skip("Live model calls disabled")
    case = load_jsonl("datasets/golden/golden.jsonl", limit=1)[0]
    output = (
        CustomerSupportLLM(AzureOpenAIModel(settings=settings))
        .answer(case.input, case.contexts)
        .answer
    )
    assert all(result.passed for result in run_deepeval_case(case, output, settings=settings))
