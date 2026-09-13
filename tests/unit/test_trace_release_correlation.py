from __future__ import annotations

import copy
import json
from pathlib import Path

from ai_quality.release_certificate import build_release_certificate
from ai_quality.release_evidence_bundle import build_release_evidence_bundle
from ai_quality.trace_release_correlation import build_runtime_trace, correlate_trace


def passport() -> dict:
    return json.loads(Path('examples/ai-system-passport.example.json').read_text(encoding='utf-8'))


def certificate_dict() -> dict:
    baseline = passport()
    candidate = copy.deepcopy(baseline)
    bundle = build_release_evidence_bundle(baseline, candidate)
    return build_release_certificate(bundle, candidate).to_dict()


def test_runtime_trace_contains_release_certificate_identity() -> None:
    cert = certificate_dict()
    trace = build_runtime_trace(trace_id='trace-001', certificate=cert)
    assert trace['release_id'] == cert['release_id']
    assert trace['certificate_id'] == cert['certificate_id']
    assert trace['release_provenance']['certificate_integrity_sha256'] == cert['integrity_sha256']


def test_trace_correlates_to_exact_certified_components() -> None:
    cert = certificate_dict()
    trace = build_runtime_trace(trace_id='trace-002', certificate=cert)
    result = correlate_trace(trace, cert)
    assert result.correlated is True
    assert result.mismatches == []


def test_trace_detects_model_version_mismatch() -> None:
    cert = certificate_dict()
    trace = build_runtime_trace(trace_id='trace-003', certificate=cert)
    trace['component_versions']['model_version'] = 'unexpected-model'
    result = correlate_trace(trace, cert)
    assert result.correlated is False
    assert any('model_version' in item for item in result.mismatches)


def test_trace_detects_wrong_release_and_certificate() -> None:
    cert = certificate_dict()
    trace = build_runtime_trace(trace_id='trace-004', certificate=cert)
    trace['release_id'] = 'rc-unknown'
    trace['certificate_id'] = 'cert-unknown'
    result = correlate_trace(trace, cert)
    assert result.correlated is False
    assert any('release_id' in item for item in result.mismatches)
    assert any('certificate_id' in item for item in result.mismatches)


def test_trace_detects_policy_version_mismatch() -> None:
    cert = certificate_dict()
    trace = build_runtime_trace(trace_id='trace-005', certificate=cert)
    trace['component_versions']['policy_version'] = 'policy-legacy'
    result = correlate_trace(trace, cert)
    assert result.correlated is False
    assert any('policy_version' in item for item in result.mismatches)
