from __future__ import annotations

import copy

from ai_quality.incident_revalidation_gate import evaluate_revalidation


def assurance() -> dict:
    return {
        'incident_id': 'inc-1',
        'release_id': 'rc-4.7.1',
        'certificate_status': 'CERTIFIED',
        'trace_correlated': True,
        'regression_asset_id': 'regression-inc-1',
    }


def regression() -> dict:
    return {
        'asset_id': 'regression-inc-1',
        'release_id': 'rc-4.7.1',
        'root_cause': {'evidence_refs': ['evidence://incident/inc-1/root-cause']},
    }


def results() -> dict:
    return {
        'revalidation_id': 'revalidate-inc-1',
        'incident_reproduction': 'pass',
        'targeted_regression': 'pass',
        'safety_regression': 'pass',
        'authorization_regression': 'pass',
        'root_cause_fix_verified': 'pass',
        'rollback_readiness': 'pass',
        'human_approval': 'pass',
        'rollback_required': False,
        'evidence_refs': ['evidence://revalidation/inc-1/tests'],
    }


def test_restore_when_all_mandatory_checks_pass() -> None:
    decision = evaluate_revalidation(
        assurance_record=assurance(), regression_asset=regression(), results=results()
    )
    assert decision.decision == 'RESTORE'
    assert decision.blockers == []


def test_hold_when_targeted_regression_fails() -> None:
    value = results()
    value['targeted_regression'] = 'fail'
    decision = evaluate_revalidation(
        assurance_record=assurance(), regression_asset=regression(), results=value
    )
    assert decision.decision == 'HOLD'
    assert 'targeted_regression failed' in decision.blockers


def test_hold_when_trace_correlation_is_invalid() -> None:
    value = assurance()
    value['trace_correlated'] = False
    decision = evaluate_revalidation(
        assurance_record=value, regression_asset=regression(), results=results()
    )
    assert decision.decision == 'HOLD'
    assert 'trace_correlation failed' in decision.blockers


def test_rollback_overrides_other_results() -> None:
    value = results()
    value['rollback_required'] = True
    decision = evaluate_revalidation(
        assurance_record=assurance(), regression_asset=regression(), results=value
    )
    assert decision.decision == 'ROLLBACK'


def test_integrity_changes_when_revalidation_evidence_changes() -> None:
    one = evaluate_revalidation(
        assurance_record=assurance(), regression_asset=regression(), results=results()
    )
    changed = copy.deepcopy(results())
    changed['human_approval'] = 'fail'
    two = evaluate_revalidation(
        assurance_record=assurance(), regression_asset=regression(), results=changed
    )
    assert one.integrity_sha256 != two.integrity_sha256
