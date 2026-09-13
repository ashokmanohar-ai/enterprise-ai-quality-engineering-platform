from __future__ import annotations

import copy
import json
from pathlib import Path

from ai_quality.passport_diff import compare_passports


EXAMPLE = Path('examples/ai-system-passport.example.json')


def _passport() -> dict:
    return json.loads(EXAMPLE.read_text(encoding='utf-8'))


def test_no_change_requires_no_action() -> None:
    baseline = _passport()
    candidate = copy.deepcopy(baseline)
    result = compare_passports(baseline, candidate)
    assert result.recommendation == 'no-change'
    assert result.changes == []


def test_rag_change_requires_monitoring() -> None:
    baseline = _passport()
    candidate = copy.deepcopy(baseline)
    candidate['components']['rag']['retriever_version'] = 'rag-v24'
    result = compare_passports(baseline, candidate)
    assert result.recommendation == 'promote-with-monitoring'
    assert result.risk_level == 'medium'


def test_safety_failure_blocks_release() -> None:
    baseline = _passport()
    candidate = copy.deepcopy(baseline)
    candidate['quality']['safety_status'] = 'fail'
    result = compare_passports(baseline, candidate)
    assert result.recommendation == 'block'
    assert 'quality.safety_status=fail' in result.new_blockers


def test_human_approval_change_requires_review() -> None:
    baseline = _passport()
    candidate = copy.deepcopy(baseline)
    candidate['human_review']['decision'] = 'pending'
    result = compare_passports(baseline, candidate)
    assert result.recommendation == 'block'
    assert result.approval_changed is True


def test_policy_change_is_high_risk_review() -> None:
    baseline = _passport()
    candidate = copy.deepcopy(baseline)
    candidate['release_gate']['policy_version'] = 'high-assurance-v4'
    result = compare_passports(baseline, candidate)
    assert result.recommendation == 'review-required'
    assert result.risk_level == 'high'
