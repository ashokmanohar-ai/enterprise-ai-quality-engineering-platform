from __future__ import annotations

import json
from pathlib import Path

from ai_quality.evaluation.contracts import SecurityFinding
from ai_quality.security.findings import normalize_finding


def normalize_garak_report(
    path: str | Path, severity_mapping: dict[str, str]
) -> list[SecurityFinding]:
    findings: list[SecurityFinding] = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        item = json.loads(line)
        if item.get("status") not in {2, "evaluated"}:
            continue
        scores = item.get("detector_results", {})
        if not any(
            float(score) > 0
            for values in scores.values()
            for score in (values if isinstance(values, list) else [values])
        ):
            continue
        probe = str(item.get("probe_classname", item.get("probe", "unknown")))
        category = (
            "prompt_injection"
            if "inject" in probe.lower() or "encoding" in probe.lower()
            else "garak_probe_hit"
        )
        findings.append(
            normalize_finding(
                framework="garak",
                category=category,
                input_text=str(item.get("prompt", "")),
                result=str(item.get("outputs", item.get("output", ""))),
                source={"probe": probe, "detectors": scores, "reproducible": True},
                severity_mapping=severity_mapping,
            )
        )
    return findings
