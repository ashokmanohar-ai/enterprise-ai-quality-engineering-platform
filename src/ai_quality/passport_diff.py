from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Change:
    path: str
    before: Any
    after: Any
    classification: str
    rationale: str


@dataclass(frozen=True)
class PassportComparison:
    recommendation: str
    risk_level: str
    changes: list[Change]
    new_blockers: list[str]
    approval_changed: bool


def _get(data: dict[str, Any], path: str) -> Any:
    value: Any = data
    for part in path.split('.'):
        if not isinstance(value, dict):
            return None
        value = value.get(part)
    return value


def _classify(path: str, before: Any, after: Any) -> tuple[str, str]:
    if before == after:
        return 'unchanged', 'No material change.'
    if path.startswith('security.'):
        return 'high', 'Security or authorization evidence changed.'
    if path.startswith('quality.'):
        return 'high', 'Evaluation evidence changed.'
    if path.startswith('release_gate.'):
        return 'high', 'Release policy or gate state changed.'
    if path.startswith('human_review.'):
        return 'high', 'Human approval state changed.'
    if path.startswith('incident.'):
        return 'high', 'Production incident posture changed.'
    if path.startswith('components.model.') or path.startswith('components.agent.'):
        return 'medium', 'Runtime behavior component changed.'
    if path.startswith('components.rag.') or path.startswith('components.prompt.'):
        return 'medium', 'Knowledge or generation configuration changed.'
    if path.startswith('components.data.'):
        return 'medium', 'Data or lineage evidence changed.'
    return 'low', 'Administrative or descriptive field changed.'


def compare_passports(baseline: dict[str, Any], candidate: dict[str, Any]) -> PassportComparison:
    tracked = [
        'identity.system_version',
        'release.commit_sha',
        'release.status',
        'components.data.dataset_id',
        'components.data.quality_status',
        'components.rag.retriever_version',
        'components.rag.index_version',
        'components.rag.embedding_model',
        'components.rag.chunking_version',
        'components.rag.groundedness',
        'components.rag.hallucination_risk',
        'components.prompt.prompt_version',
        'components.prompt.template_hash',
        'components.model.model_version',
        'components.model.provider',
        'components.agent.agent_version',
        'components.agent.mcp_servers',
        'components.agent.tools',
        'components.agent.tool_policy_version',
        'security.least_privilege_status',
        'security.confused_deputy_check',
        'security.policy_violations',
        'quality.functional_status',
        'quality.safety_status',
        'quality.groundedness_status',
        'quality.agent_task_success_status',
        'quality.performance_status',
        'quality.blocking_findings',
        'human_review.required',
        'human_review.decision',
        'release_gate.policy_version',
        'release_gate.gate_status',
        'release_gate.rollback_plan_id',
        'observability.slo_status',
        'observability.drift_status',
        'observability.cost_status',
        'incident.active_critical_incident',
        'assurance.overall_status',
    ]

    changes: list[Change] = []
    for path in tracked:
        before = _get(baseline, path)
        after = _get(candidate, path)
        if before == after:
            continue
        classification, rationale = _classify(path, before, after)
        changes.append(Change(path, before, after, classification, rationale))

    blockers: list[str] = []
    for path in (
        'components.data.quality_status',
        'security.least_privilege_status',
        'security.confused_deputy_check',
        'quality.functional_status',
        'quality.safety_status',
        'quality.groundedness_status',
        'quality.agent_task_success_status',
        'quality.performance_status',
        'release_gate.gate_status',
    ):
        value = _get(candidate, path)
        if value == 'fail':
            blockers.append(f'{path}=fail')

    if _get(candidate, 'security.policy_violations'):
        blockers.append('security.policy_violations present')
    if _get(candidate, 'quality.blocking_findings'):
        blockers.append('quality.blocking_findings present')
    if _get(candidate, 'incident.active_critical_incident') is True:
        blockers.append('active critical incident')
    if _get(candidate, 'human_review.required') and _get(candidate, 'human_review.decision') != 'approved':
        blockers.append('required human approval not satisfied')

    approval_changed = (
        _get(baseline, 'human_review.decision') != _get(candidate, 'human_review.decision')
    )

    severities = {change.classification for change in changes}
    risk_level = 'high' if 'high' in severities else 'medium' if 'medium' in severities else 'low'

    if blockers:
        recommendation = 'block'
    elif risk_level == 'high' or approval_changed:
        recommendation = 'review-required'
    elif changes:
        recommendation = 'promote-with-monitoring'
    else:
        recommendation = 'no-change'

    return PassportComparison(
        recommendation=recommendation,
        risk_level=risk_level,
        changes=changes,
        new_blockers=blockers,
        approval_changed=approval_changed,
    )
