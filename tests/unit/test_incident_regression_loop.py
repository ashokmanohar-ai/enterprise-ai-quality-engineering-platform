from __future__ import annotations

import json
from pathlib import Path

from ai_quality.incident_regression_loop import build_incident_assurance_record, build_regression_asset
from ai_quality.release_certificate import build_release_certificate
from ai_quality.release_evidence_bundle import build_release_evidence_bundle
from ai_quality.trace_release_correlation import build_runtime_trace, correlate_trace


def load(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding='utf-8'))


def setup_chain() -> tuple[dict, dict, dict, dict]:
    baseline = load('examples/ai-system-passport.baseline.json')
    candidate = load('examples/ai-system-passport.candidate.json')
    incident = load('examples/incident-regression.example.json')
    bundle = build_release_evidence_bundle(baseline, candidate)
    certificate = build_release_certificate(bundle, candidate)
    trace = build_runtime_trace(trace_id='trace-prod-demo-001', certificate=certificate.to_dict())
    correlation = correlate_trace(trace, certificate.to_dict())
    return incident, trace, correlation.to_dict(), certificate.to_dict()


def test_builds_regression_asset_with_provenance() -> None:
    incident, trace, correlation, certificate = setup_chain()
    asset = build_regression_asset(
        incident=incident,
        trace=trace,
        correlation=correlation,
        certificate=certificate,
    )
    assert asset.asset_id == 'regression-INC-2026-0914-001'
    assert asset.trace_id == 'trace-prod-demo-001'
    assert asset.provenance['trace_correlation_valid'] is True
    assert asset.provenance['certificate_integrity_sha256']


def test_regression_asset_carries_root_cause_and_assertions() -> None:
    incident, trace, correlation, certificate = setup_chain()
    asset = build_regression_asset(
        incident=incident,
        trace=trace,
        correlation=correlation,
        certificate=certificate,
    )
    assert asset.root_cause['component'] == 'rag'
    assert 'correct policy source ranked in top-3' in asset.expected_behavior['blocking_assertions']


def test_incident_record_links_release_certificate_and_regression() -> None:
    incident, trace, correlation, certificate = setup_chain()
    record = build_incident_assurance_record(
        incident=incident,
        trace=trace,
        correlation=correlation,
        certificate=certificate,
    )
    assert record['release_id'] == 'rc-4.7.1'
    assert record['certificate_id'] == 'cert-rc-4.7.1'
    assert record['regression_asset_id'] == 'regression-INC-2026-0914-001'
    assert record['release_action'] == 'hold-and-revalidate'


def test_integrity_changes_when_expected_behavior_changes() -> None:
    incident, trace, correlation, certificate = setup_chain()
    first = build_regression_asset(
        incident=incident,
        trace=trace,
        correlation=correlation,
        certificate=certificate,
    )
    changed = json.loads(json.dumps(incident))
    changed['expected_behavior']['expected_result'] = 'A different expected result.'
    second = build_regression_asset(
        incident=changed,
        trace=trace,
        correlation=correlation,
        certificate=certificate,
    )
    assert first.integrity_sha256 != second.integrity_sha256


def test_mismatch_is_preserved_in_regression_provenance() -> None:
    incident, trace, correlation, certificate = setup_chain()
    correlation['correlated'] = False
    correlation['mismatches'] = ['model_version mismatch']
    asset = build_regression_asset(
        incident=incident,
        trace=trace,
        correlation=correlation,
        certificate=certificate,
    )
    assert asset.provenance['trace_correlation_valid'] is False
    assert asset.provenance['trace_mismatches'] == ['model_version mismatch']
