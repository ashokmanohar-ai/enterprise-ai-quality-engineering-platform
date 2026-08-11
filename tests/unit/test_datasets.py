from ai_quality.evaluation.datasets import load_jsonl, to_deepeval, to_promptfoo, to_ragas


def test_required_dataset_sizes() -> None:
    assert len(load_jsonl("datasets/golden/golden.jsonl")) >= 30
    assert len(load_jsonl("datasets/agents/agent-cases.jsonl")) >= 15
    assert len(load_jsonl("datasets/security/security-cases.jsonl")) >= 20


def test_one_canonical_case_adapts_without_mutation() -> None:
    case = load_jsonl("datasets/golden/golden.jsonl", limit=1)[0]
    assert to_deepeval(case, "answer")["input"] == case.input
    assert to_ragas(case, "answer", ["context"])["reference"] == case.reference_answer
    assert to_promptfoo(case)["description"] == case.id


def test_ids_are_unique() -> None:
    for path in (
        "datasets/golden/golden.jsonl",
        "datasets/agents/agent-cases.jsonl",
        "datasets/security/security-cases.jsonl",
    ):
        cases = load_jsonl(path)
        assert len({case.id for case in cases}) == len(cases)
