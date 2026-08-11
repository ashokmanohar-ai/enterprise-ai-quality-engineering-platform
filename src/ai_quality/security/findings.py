from __future__ import annotations

import hashlib
from typing import Any

from ai_quality.evaluation.contracts import SecurityFinding, Severity


def normalize_finding(
    *,
    framework: str,
    category: str,
    input_text: str,
    result: str,
    source: dict[str, Any],
    severity_mapping: dict[str, str],
) -> SecurityFinding:
    native_severity = source.get("severity")
    mapped = False
    severity: Severity | None = None
    if native_severity and str(native_severity).lower() in Severity._value2member_map_:
        severity = Severity(str(native_severity).lower())
    elif category in severity_mapping:
        severity = Severity(severity_mapping[category])
        mapped = True
    identifier = hashlib.sha256(f"{framework}:{category}:{input_text}".encode()).hexdigest()[:16]
    return SecurityFinding(
        id=f"{framework}-{identifier}",
        framework=framework,
        category=category,
        severity=severity,
        input=input_text,
        result=result,
        reproducible=bool(source.get("reproducible", True)),
        blocking=severity in {Severity.HIGH, Severity.CRITICAL},
        source_severity=str(native_severity) if native_severity else None,
        internal_mapping_applied=mapped,
        metadata=source,
    )
