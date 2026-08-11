from pathlib import Path


def test_candidate_prompt_preserves_enterprise_controls() -> None:
    candidate = Path("prompts/customer-support/v2.txt").read_text(encoding="utf-8").lower()
    for control in ("only supplied policy", "never reveal", "authorization", "confirmation"):
        assert control in candidate


def test_prompt_versions_are_distinct() -> None:
    assert (
        Path("prompts/customer-support/v1.txt").read_bytes()
        != Path("prompts/customer-support/v2.txt").read_bytes()
    )
