from __future__ import annotations

from ai_quality.release_assurance_visualization import build_timeline, render_release_assurance_html


def fixtures():
    passport = {
        'release': {'release_id': 'rc-1'},
        'assurance': {'overall_status': 'release-ready'},
    }
    certificate = {'certificate_id': 'cert-rc-1', 'status': 'CERTIFIED'}
    trace = {'trace_id': 'trace-1', 'correlated': True}
    incident = {'incident_id': 'INC-1', 'status': 'contained'}
    regression = {'asset_id': 'regression-INC-1'}
    revalidation = {'revalidation_id': 'revalidate-INC-1', 'decision': 'RESTORE'}
    trust = {
        'system_id': 'system-1',
        'release_id': 'rc-1',
        'trust_status': 'TRUSTED',
        'trust_score': 100,
        'hard_blockers': [],
        'warnings': [],
        'factors': {'quality': 15},
        'nodes': [
            {'node_id': 'passport:rc-1', 'node_type': 'passport', 'status': 'release-ready', 'integrity_sha256': None},
            {'node_id': 'cert-rc-1', 'node_type': 'certificate', 'status': 'CERTIFIED', 'integrity_sha256': 'abc'},
        ],
        'edges': [
            {'source': 'passport:rc-1', 'target': 'cert-rc-1', 'relation': 'certified-as'},
        ],
    }
    return passport, certificate, trace, incident, regression, revalidation, trust


def test_timeline_has_complete_closed_loop_order() -> None:
    passport, certificate, trace, incident, regression, revalidation, trust = fixtures()
    timeline = build_timeline(
        passport=passport,
        certificate=certificate,
        trace_correlation=trace,
        incident_record=incident,
        regression_asset=regression,
        revalidation=revalidation,
        trust_assessment=trust,
    )
    assert [stage['stage'] for stage in timeline] == [
        'System Passport', 'Release Certificate', 'Production Trace', 'Incident',
        'Regression Asset', 'Revalidation', 'Trust Recalculation',
    ]
    assert timeline[-1]['status'] == 'TRUSTED'


def test_html_contains_trust_score_and_graph() -> None:
    passport, certificate, trace, incident, regression, revalidation, trust = fixtures()
    html = render_release_assurance_html(
        passport=passport,
        certificate=certificate,
        trace_correlation=trace,
        incident_record=incident,
        regression_asset=regression,
        revalidation=revalidation,
        trust_assessment=trust,
    )
    assert '100<small>/100</small>' in html
    assert 'Evidence nodes' in html
    assert 'certified-as' in html
    assert 'Governance rule' in html


def test_html_escapes_untrusted_values() -> None:
    passport, certificate, trace, incident, regression, revalidation, trust = fixtures()
    incident['incident_id'] = '<script>alert(1)</script>'
    html = render_release_assurance_html(
        passport=passport,
        certificate=certificate,
        trace_correlation=trace,
        incident_record=incident,
        regression_asset=regression,
        revalidation=revalidation,
        trust_assessment=trust,
    )
    assert '<script>alert(1)</script>' not in html
    assert '&lt;script&gt;alert(1)&lt;/script&gt;' in html


def test_blockers_are_visible_even_with_high_score() -> None:
    passport, certificate, trace, incident, regression, revalidation, trust = fixtures()
    trust['trust_status'] = 'BLOCKED'
    trust['trust_score'] = 95
    trust['hard_blockers'] = ['safety controls are not passing']
    html = render_release_assurance_html(
        passport=passport,
        certificate=certificate,
        trace_correlation=trace,
        incident_record=incident,
        regression_asset=regression,
        revalidation=revalidation,
        trust_assessment=trust,
    )
    assert 'BLOCKED' in html
    assert 'safety controls are not passing' in html
    assert 'Hard blockers' in html
