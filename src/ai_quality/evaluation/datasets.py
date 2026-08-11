from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path

from ai_quality.config import ROOT
from ai_quality.evaluation.contracts import CanonicalCase


def load_jsonl(path: str | Path, *, limit: int | None = None) -> list[CanonicalCase]:
    resolved = Path(path)
    if not resolved.is_absolute():
        resolved = ROOT / resolved
    cases: list[CanonicalCase] = []
    with resolved.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            try:
                cases.append(CanonicalCase.model_validate_json(line))
            except Exception as exc:
                raise ValueError(
                    f"Invalid canonical case at {resolved}:{line_number}: {exc}"
                ) from exc
            if limit is not None and len(cases) >= limit:
                break
    return cases


def dump_jsonl(cases: Iterable[CanonicalCase], path: str | Path) -> None:
    resolved = Path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    with resolved.open("w", encoding="utf-8") as handle:
        for case in cases:
            handle.write(case.model_dump_json() + "\n")


def dataset_version(path: str | Path) -> str:
    import hashlib

    resolved = Path(path)
    if not resolved.is_absolute():
        resolved = ROOT / resolved
    return hashlib.sha256(resolved.read_bytes()).hexdigest()[:12]


def to_deepeval(case: CanonicalCase, actual_output: str) -> dict[str, object]:
    return {
        "input": case.input,
        "actual_output": actual_output,
        "expected_output": case.reference_answer,
        "context": case.contexts,
        "retrieval_context": case.contexts,
    }


def to_ragas(
    case: CanonicalCase, actual_output: str, retrieved_contexts: list[str]
) -> dict[str, object]:
    return {
        "user_input": case.input,
        "response": actual_output,
        "reference": case.reference_answer,
        "retrieved_contexts": retrieved_contexts,
        "reference_contexts": case.contexts,
    }


def to_promptfoo(case: CanonicalCase) -> dict[str, object]:
    assertions: list[dict[str, object]] = []
    assertions.extend(
        {"type": "icontains", "value": value} for value in case.expected_behavior.must_include
    )
    assertions.extend(
        {"type": "not-icontains", "value": value} for value in case.expected_behavior.must_not_claim
    )
    if case.reference_answer:
        assertions.append(
            {"type": "llm-rubric", "value": f"Answer is consistent with: {case.reference_answer}"}
        )
    return {
        "description": case.id,
        "vars": {"question": case.input, "contexts": "\n".join(case.contexts)},
        "assert": assertions,
    }


def export_promptfoo(cases: Iterable[CanonicalCase], path: str | Path) -> None:
    resolved = Path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    resolved.write_text(
        json.dumps([to_promptfoo(case) for case in cases], indent=2), encoding="utf-8"
    )
