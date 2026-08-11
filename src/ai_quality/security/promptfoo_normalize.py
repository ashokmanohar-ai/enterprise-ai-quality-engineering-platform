from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ai_quality.evaluation.contracts import SecurityFinding
from ai_quality.security.findings import normalize_finding


def _rows(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [row for row in payload if isinstance(row, dict)]
    if not isinstance(payload, dict):
        return []
    for path in (("results", "results"), ("results",), ("data", "results")):
        current: Any = payload
        for key in path:
            current = current.get(key, {}) if isinstance(current, dict) else {}
        if isinstance(current, list):
            return [row for row in current if isinstance(row, dict)]
    return []


def normalize_promptfoo_report(
    path: str | Path,
    severity_mapping: dict[str, str],
) -> list[SecurityFinding]:
    text = Path(path).read_text(encoding="utf-8")
    try:
        payload: Any = json.loads(text)
        rows = _rows(payload)
    except json.JSONDecodeError:
        rows = [json.loads(line) for line in text.splitlines() if line.strip()]
    findings: list[SecurityFinding] = []
    for row in rows:
        success = row.get("success", row.get("pass", row.get("gradingResult", {}).get("pass")))
        if success is not False:
            continue
        metadata = row.get("metadata", {})
        category = str(
            metadata.get("pluginId")
            or metadata.get("plugin")
            or row.get("pluginId")
            or row.get("metric")
            or "promptfoo_redteam_failure"
        ).replace("-", "_")
        prompt = row.get("prompt", row.get("vars", {}).get("prompt", ""))
        output = (
            row.get("response", {}).get("output")
            if isinstance(row.get("response"), dict)
            else row.get("output", row.get("response", ""))
        )
        source = {"reproducible": True, **row}
        findings.append(
            normalize_finding(
                framework="promptfoo",
                category=category,
                input_text=str(prompt),
                result=str(output),
                source=source,
                severity_mapping=severity_mapping,
            )
        )
    return findings
