from ai_quality.config import Settings


def test_safe_summary_never_contains_key() -> None:
    settings = Settings(
        azure_openai_api_key="super-secret",
        azure_openai_endpoint="https://example.openai.azure.com/",
    )
    text = str(settings.safe_summary())
    assert "super-secret" not in text
    assert settings.azure_openai_endpoint == "https://example.openai.azure.com"


def test_live_calls_are_off_by_default() -> None:
    assert Settings().aiq_allow_live_model_calls is False
