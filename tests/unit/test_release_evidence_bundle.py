from __future__ import annotations

import copy
import json
from pathlib import Path

from ai_quality.release_evidence_bundle import build_release_evidence_bundle


EXAMPLE = Path("examples/ai-system-passport.example.json")


def passport() -> dict:
    return json.loads(EXAMPLE.read_text(encoding="utf-8"))


def test_bundle_contains_release_identity_and_integrity() -> None:
    base = passport()
    bundle = build_release_evidence_bundle(base, copy.deepcopy(base))
    assert bundle.system_id == "acme-support-ai"
    assert bundle.release_id == "rc-4.7.1"
    assert len(bundle.integrity_sha256) == 64


def test_bundle_carries_human_approval_and_rollback_plan() -> None:
    base = passport()
    bundle = build_release_evidence_bundle(base, copy.deepcopy(base))
    assert bundle.human_approval["decision"] == "approved"
    assert bundle.rollback_plan["rollback_plan_id"] == "rollback-4.7.1"


def test_bundle_blocks_when_candidate_passport_blocks() -> None:
    base = passport()
    candidate = copy.deepcopy(base)
    candidate["quality"]["safety_status"] = "fail"
    bundle = build_release_evidence_bundle(base, candidate)
    assert bundle.release_recommendation == "block"


def test_bundle_deduplicates_evidence_references() -> None:
    base = passport()
    candidate = copy.deepcopy(base)
    candidate["assurance"]["evidence_refs"].append("evidence://release/bundle-rc-4.7.1")
    bundle = build_release_evidence_bundle(base, candidate)
    assert len(bundle.evidence_refs) == len(set(bundle.evidence_refs))


def test_bundle_is_deterministic_except_generation_time() -> None:
    base = passport()
    one = build_release_evidence_bundle(base, copy.deepcopy(base)).to_dict()
    two = build_release_evidence_bundle(base, copy.deepcopy(base)).to_dict()
    one.pop("generated_at")
    two.pop("generated_at")
    one.pop("integrity_sha256")
    two.pop("integrity_sha256")
    assert one == two
