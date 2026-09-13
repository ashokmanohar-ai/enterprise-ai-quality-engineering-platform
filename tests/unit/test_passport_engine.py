from __future__ import annotations

import copy
import json
from pathlib import Path

from ai_quality.passport_engine import evaluate_passport


def _passport() -> dict:
    return json.loads(Path('examples/ai-system-passport.example.json').read_text(encoding='utf-8'))


def test_reference_passport_is_release_ready() -> None:
    decision = evaluate_passport(_passport())
    assert decision.status == 'release-ready'
    assert not decision.reasons


def test_safety_failure_blocks_release() -> None:
    passport = _passport()
    passport['quality']['safety_status'] = 'fail'
    decision = evaluate_passport(passport)
    assert decision.status == 'blocked'
    assert any('safety quality failed' in reason for reason in decision.reasons)


def test_missing_human_approval_blocks_release() -> None:
    passport = _passport()
    passport['human_review']['decision'] = 'pending'
    decision = evaluate_passport(passport)
    assert decision.status == 'blocked'


def test_warning_produces_conditional_decision() -> None:
    passport = _passport()
    passport['quality']['performance_status'] = 'warn'
    decision = evaluate_passport(passport)
    assert decision.status == 'conditional'
    assert decision.warnings


def test_rollback_is_explicit_state() -> None:
    passport = copy.deepcopy(_passport())
    passport['incident']['rollback_executed'] = True
    decision = evaluate_passport(passport)
    assert decision.status == 'rolled-back'
