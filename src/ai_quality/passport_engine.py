from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

DecisionStatus = Literal['release-ready', 'conditional', 'blocked', 'rolled-back']


@dataclass(frozen=True)
class PassportDecision:
    status: DecisionStatus
    reasons: tuple[str, ...]
    warnings: tuple[str, ...]


def _get(data: dict[str, Any], *path: str, default: Any = None) -> Any:
    value: Any = data
    for key in path:
        if not isinstance(value, dict) or key not in value:
            return default
        value = value[key]
    return value


def validate_passport(passport: dict[str, Any]) -> list[str]:
    required = [
        'passport_version', 'identity', 'release', 'components', 'security',
        'quality', 'human_review', 'release_gate', 'observability', 'incident', 'assurance'
    ]
    errors = [f'Missing field: {key}' for key in required if key not in passport]
    if passport.get('passport_version') != '1.0':
        errors.append("passport_version must be '1.0'")
    for path in [
        ('identity', 'system_id'), ('identity', 'system_version'),
        ('release', 'release_id'), ('release', 'commit_sha'),
        ('quality', 'evaluation_id'), ('release_gate', 'policy_version'),
        ('release_gate', 'rollback_plan_id'),
    ]:
        if not _get(passport, *path):
            errors.append(f"Missing required value: {'.'.join(path)}")
    return errors


def evaluate_passport(passport: dict[str, Any]) -> PassportDecision:
    errors = validate_passport(passport)
    if errors:
        return PassportDecision('blocked', tuple(errors), ())

    if _get(passport, 'release', 'status') == 'rolled-back' or _get(
        passport, 'incident', 'rollback_executed', default=False
    ):
        return PassportDecision('rolled-back', ('Rollback is recorded.',), ())

    reasons: list[str] = []
    warnings: list[str] = []

    mandatory = {
        'data quality': _get(passport, 'components', 'data', 'quality_status'),
        'least privilege': _get(passport, 'security', 'least_privilege_status'),
        'delegation boundary': _get(passport, 'security', 'confused_deputy_check'),
        'functional quality': _get(passport, 'quality', 'functional_status'),
        'safety quality': _get(passport, 'quality', 'safety_status'),
        'groundedness': _get(passport, 'quality', 'groundedness_status'),
        'agent task success': _get(passport, 'quality', 'agent_task_success_status'),
    }
    advisory = {
        'performance': _get(passport, 'quality', 'performance_status'),
        'SLO': _get(passport, 'observability', 'slo_status'),
        'drift': _get(passport, 'observability', 'drift_status'),
        'cost': _get(passport, 'observability', 'cost_status'),
    }

    for label, status in mandatory.items():
        if status == 'fail':
            reasons.append(f'{label} failed')
        elif status != 'pass':
            warnings.append(f'{label} is {status or "missing"}')

    for label, status in advisory.items():
        if status != 'pass':
            warnings.append(f'{label} is {status or "missing"}')

    if _get(passport, 'security', 'policy_violations', default=[]):
        reasons.append('Policy violations are present')
    if _get(passport, 'quality', 'blocking_findings', default=[]):
        reasons.append('Blocking quality findings are present')
    if _get(passport, 'incident', 'active_critical_incident', default=False):
        reasons.append('An active critical incident exists')

    if _get(passport, 'human_review', 'required', default=False) and _get(
        passport, 'human_review', 'decision'
    ) != 'approved':
        reasons.append('Required human approval is not satisfied')

    gate = _get(passport, 'release_gate', 'gate_status')
    if gate == 'fail':
        reasons.append('Release gate failed')
    elif gate != 'pass':
        warnings.append(f'Release gate is {gate or "missing"}')

    if _get(passport, 'assurance', 'exceptions', default=[]):
        warnings.append('Assurance exceptions are present')

    if reasons:
        return PassportDecision('blocked', tuple(reasons), tuple(warnings))
    if warnings:
        return PassportDecision('conditional', (), tuple(warnings))
    return PassportDecision('release-ready', (), ())
