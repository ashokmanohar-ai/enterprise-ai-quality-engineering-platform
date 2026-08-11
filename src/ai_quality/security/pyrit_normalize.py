from __future__ import annotations

from typing import Any

from ai_quality.evaluation.contracts import SecurityFinding
from ai_quality.security.findings import normalize_finding


def normalize_pyrit_result(
    result: Any,
    *,
    objective: str,
    category: str,
    severity_mapping: dict[str, str],
) -> SecurityFinding | None:
    outcome = str(getattr(result, "outcome", getattr(result, "status", "unknown"))).lower()
    achieved = bool(getattr(result, "objective_achieved", False)) or outcome in {
        "success",
        "achieved",
        "true",
    }
    if not achieved:
        return None
    return normalize_finding(
        framework="pyrit",
        category=category,
        input_text=objective,
        result=str(getattr(result, "last_response", getattr(result, "conversation_id", outcome))),
        source={"outcome": outcome, "reproducible": True},
        severity_mapping=severity_mapping,
    )
