from __future__ import annotations

import json
from pathlib import Path

from ai_quality.release_trust_graph import build_release_trust_assessment


def load_candidate() -> dict:
    return json.loads(Path('examples/ai-system-passport.candidate.json').read_text())


def certificate(status: str = 'CERTIFIED') -> dict:
    return {
        'certificate_id': 'cert-rc-4.7.1',
        'status': status,
        'integrity_sha256': 'abc123',
    }


def trace(correlated: bool = True) -> dict:
    return {'trace_id': 'trace-1', 'correlated': correlated}


def test_trusted_release_without_blockers() -> None:
    result = build_release_trust_assessment(
        passport=load_candidate(), certificate=certificate(), trace_correlation=trace()
    )
    assert result.trust_status in {'TRUSTED', 'CONDITIONAL'}
    assert result.trust_score >= 90
    assert not result.hard_blockers


def test_trace_mismatch_is_hard_blocker() -> None:
    result = build_release_trust_assessment(
        passport=load_candidate(), certificate=certificate(), trace_correlation=trace(False)
    )
    assert result.trust_status == 'BLOCKED'
    assert any('trace' in item for item in result.hard_blockers)


def test_blocked_certificate_cannot_be_overridden_by_score() -> None:
    result = build_release_trust_assessment(
        passport=load_candidate(), certificate=certificate('BLOCKED'), trace_correlation=trace()
    )
    assert result.trust_status == 'BLOCKED'
    assert 'release certificate is BLOCKED' in result.hard_blockers


def test_incident_requires_restore_decision() -> None:
    result = build_release_trust_assessment(
        passport=load_candidate(),
        certificate=certificate(),
        trace_correlation=trace(),
        incident_record={'incident_id': 'inc-1', 'status': 'mitigated'},
        regression_asset={'asset_id': 'regression-inc-1', 'integrity_sha256': 'reg123'},
        revalidation={'revalidation_id': 'rev-1', 'decision': 'HOLD', 'integrity_sha256': 'rev123'},
    )
    assert result.trust_status == 'BLOCKED'
    assert any('HOLD' in item for item in result.hard_blockers)


def test_graph_links_full_recovery_chain() -> None:
    result = build_release_trust_assessment(
        passport=load_candidate(),
        certificate=certificate(),
        trace_correlation=trace(),
        incident_record={'incident_id': 'inc-1', 'status': 'resolved'},
        regression_asset={'asset_id': 'regression-inc-1', 'integrity_sha256': 'reg123'},
        revalidation={'revalidation_id': 'rev-1', 'decision': 'RESTORE', 'integrity_sha256': 'rev123'},
    )
    node_types = {node.node_type for node in result.nodes}
    assert {'passport', 'certificate', 'trace', 'incident', 'regression_asset', 'revalidation'} <= node_types
    assert any(edge.relation == 'revalidated-by' for edge in result.edges)
