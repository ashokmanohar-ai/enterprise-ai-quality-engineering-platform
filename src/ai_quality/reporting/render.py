from __future__ import annotations

import json
from pathlib import Path

from ai_quality.config import ROOT
from ai_quality.evaluation.contracts import QualityReport


def write_report(
    report: QualityReport, directory: str | Path = "reports/summary"
) -> tuple[Path, Path]:
    resolved = Path(directory)
    if not resolved.is_absolute():
        resolved = ROOT / resolved
    resolved.mkdir(parents=True, exist_ok=True)
    json_path = resolved / "quality-report.json"
    markdown_path = resolved / "quality-report.md"
    json_path.write_text(report.model_dump_json(indent=2), encoding="utf-8")
    lines = [
        "# Enterprise AI Quality Gate",
        "",
        f"**Deployment decision: {'APPROVED' if report.status == 'PASS' else 'BLOCKED'}**",
        "",
        "| Dimension | Status |",
        "|---|---|",
    ]
    lines.extend(
        f"| {name.replace('_', ' ').title()} | {status} |"
        for name, status in report.summary.items()
    )
    lines.extend(["", "## Blocking findings", ""])
    if report.blocking_failures:
        lines.extend(
            f"- **{item.framework} / {item.metric} / {item.test_id}:** {item.reason}"
            for item in report.blocking_failures
        )
    else:
        lines.append("None.")
    lines.extend(
        [
            "",
            "## Reproducibility",
            "",
            "```json",
            json.dumps(report.metadata.model_dump(mode="json"), indent=2),
            "```",
            "",
        ]
    )
    markdown_path.write_text("\n".join(lines), encoding="utf-8")
    return json_path, markdown_path
