from __future__ import annotations

import argparse
import json
from pathlib import Path

from ai_quality.release_evidence_bundle import build_release_evidence_bundle


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Build an auditable AI release evidence bundle.")
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("reports/release-evidence-bundle.json"))
    parser.add_argument("--markdown", type=Path, default=Path("reports/release-evidence-bundle.md"))
    args = parser.parse_args()

    bundle = build_release_evidence_bundle(load_json(args.baseline), load_json(args.candidate))
    payload = bundle.to_dict()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# AI Release Evidence Bundle",
        "",
        f"- **Bundle ID:** `{payload['bundle_id']}`",
        f"- **System:** `{payload['system_id']}`",
        f"- **Release:** `{payload['release_id']}`",
        f"- **Commit:** `{payload['commit_sha']}`",
        f"- **Passport decision:** `{payload['passport_decision']['status']}`",
        f"- **Release recommendation:** `{payload['release_recommendation']}`",
        f"- **Integrity SHA-256:** `{payload['integrity_sha256']}`",
        "",
        "## Human approval",
        "",
        f"- Required: `{payload['human_approval']['required']}`",
        f"- Decision: `{payload['human_approval']['decision']}`",
        f"- Reviewer: `{payload['human_approval'].get('reviewer')}`",
        "",
        "## Rollback plan",
        "",
        f"- Plan ID: `{payload['rollback_plan'].get('rollback_plan_id')}`",
        f"- Executed: `{payload['rollback_plan'].get('rollback_executed')}`",
        f"- Revalidation ID: `{payload['rollback_plan'].get('revalidation_id')}`",
        "",
        "## Evidence references",
        "",
    ]
    lines.extend(f"- `{ref}`" for ref in payload["evidence_refs"])
    args.markdown.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps({
        "bundle_id": payload["bundle_id"],
        "passport_status": payload["passport_decision"]["status"],
        "recommendation": payload["release_recommendation"],
        "integrity_sha256": payload["integrity_sha256"],
    }, indent=2))

    return 1 if payload["release_recommendation"] == "block" else 0


if __name__ == "__main__":
    raise SystemExit(main())
