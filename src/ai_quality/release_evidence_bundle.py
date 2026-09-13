from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from hashlib import sha256
from typing import Any
import json

from ai_quality.passport_engine import evaluate_passport
from ai_quality.passport_diff import compare_passports


@dataclass(frozen=True)
class ReleaseEvidenceBundle:
    bundle_version: str
    bundle_id: str
    generated_at: str
    system_id: str
    release_id: str
    commit_sha: str
    passport_decision: dict[str, Any]
    release_comparison: dict[str, Any]
    human_approval: dict[str, Any]
    rollback_plan: dict[str, Any]
    release_recommendation: str
    evidence_refs: list[str]
    integrity_sha256: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _canonical_json(value: dict[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _bundle_integrity(payload: dict[str, Any]) -> str:
    return sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def build_release_evidence_bundle(
    baseline: dict[str, Any],
    candidate: dict[str, Any],
) -> ReleaseEvidenceBundle:
    passport_decision = evaluate_passport(candidate).to_dict()
    comparison = compare_passports(baseline, candidate).to_dict()

    identity = candidate["identity"]
    release = candidate["release"]
    approval = candidate["human_review"]
    release_gate = candidate["release_gate"]

    rollback_plan = {
        "rollback_plan_id": release_gate.get("rollback_plan_id"),
        "rollback_executed": candidate["incident"].get("rollback_executed", False),
        "revalidation_id": candidate["incident"].get("revalidation_id"),
    }

    recommendation = comparison["recommendation"]
    if passport_decision["status"] in {"blocked", "rolled-back"}:
        recommendation = "block"

    evidence_refs = list(candidate["assurance"].get("evidence_refs", []))
    if release_gate.get("evidence_bundle_id"):
        evidence_refs.append(f"evidence://bundle/{release_gate['evidence_bundle_id']}")

    base_payload: dict[str, Any] = {
        "bundle_version": "1.0",
        "bundle_id": f"bundle-{release['release_id']}",
        "generated_at": datetime.now(UTC).isoformat(),
        "system_id": identity["system_id"],
        "release_id": release["release_id"],
        "commit_sha": release["commit_sha"],
        "passport_decision": passport_decision,
        "release_comparison": comparison,
        "human_approval": approval,
        "rollback_plan": rollback_plan,
        "release_recommendation": recommendation,
        "evidence_refs": sorted(set(evidence_refs)),
    }
    integrity = _bundle_integrity(base_payload)
    return ReleaseEvidenceBundle(**base_payload, integrity_sha256=integrity)
