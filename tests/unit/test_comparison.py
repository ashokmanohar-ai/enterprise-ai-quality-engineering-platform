from ai_quality.experiments.comparison import compare_baseline


def test_critical_regression_blocks() -> None:
    comparison = compare_baseline(
        {"faithfulness": 0.90},
        {"faithfulness": 0.80},
        max_quality_drop=0.03,
        critical_metrics={"faithfulness"},
    )
    assert comparison[0]["classification"] == "blocking_regression"


def test_small_change_is_neutral() -> None:
    comparison = compare_baseline({"relevance": 0.80}, {"relevance": 0.79}, max_quality_drop=0.03)
    assert comparison[0]["classification"] == "neutral"
