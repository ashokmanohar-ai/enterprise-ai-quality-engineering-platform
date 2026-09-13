from __future__ import annotations

import copy
import json
from pathlib import Path

from ai_quality.release_certificate import build_release_certificate
from ai_quality.release_evidence_bundle import build_release_evidence_bundle


def passport() -> dict:
    return json.loads(Path('examples/ai-system-passport.example.json').read_text(encoding='utf-8'))


def certificate(candidate: dict):
    base = passport()
    bundle = build_release_evidence_bundle(base, candidate)
    return build_release_certificate(bundle, candidate)


def test_certificate_is_certified_for_release_ready_no_change() -> None:
    candidate = passport()
    cert = certificate(candidate)
    assert cert.status == 'CERTIFIED'
    assert cert.provenance['source_bundle_id'] == 'bundle-rc-4.7.1'


def test_certificate_is_blocked_for_safety_failure() -> None:
    candidate = passport()
    candidate['quality']['safety_status'] = 'fail'
    cert = certificate(candidate)
    assert cert.status == 'BLOCKED'


def test_certificate_is_conditional_for_warning() -> None:
    candidate = passport()
    candidate['observability']['cost_status'] = 'warn'
    cert = certificate(candidate)
    assert cert.status == 'CONDITIONAL'


def test_certificate_carries_component_versions() -> None:
    candidate = passport()
    cert = certificate(candidate)
    assert cert.component_summary['prompt_version'] == 'prompt-v12'
    assert cert.component_summary['agent_version'] == 'agent-v9'


def test_certificate_integrity_changes_when_evidence_changes() -> None:
    candidate = passport()
    one = certificate(candidate)
    changed = copy.deepcopy(candidate)
    changed['components']['prompt']['prompt_version'] = 'prompt-v13'
    two = certificate(changed)
    assert one.integrity_sha256 != two.integrity_sha256
