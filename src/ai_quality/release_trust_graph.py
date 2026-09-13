from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from typing import Any, Literal

TrustStatus = Literal['TRUSTED', 'CONDITIONAL', 'BLOCKED']


@dataclass(frozen=True)
class EvidenceNode:
    node_id: str
    node_type: str
    status: str
    integrity_sha256: str | None


@dataclass(frozen=True)
class EvidenceEdge:
    source: str
    target: str
    relation: str


@dataclass(frozen=True)
class ReleaseTrustAssessment:
    assessment_version: str
    system_id: str
    release_id: str
    trust_score: int
    trust_status: TrustStatus
    hard_blockers: list[str]
    warnings: list[str]
    factors: dict[str, int]
    nodes: list[EvidenceNode]
    edges: list[EvidenceEdge]
    integrity_sha256: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _canonical(value: dict[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True)


def _hash(value: dict[str, Any]) -> str:
    return sha256(_canonical(value).encode('utf-8')).hexdigest()


def _factor(status: bool, pass_score: int) -> int:
    return pass_score if status else 0


def build_release_trust_assessment(
    *,
    passport: dict[str, Any],
    certificate: dict[str, Any],
    trace_correlation: dict[str, Any],
    incident_record: dict[str, Any] | None = None,
    regression_asset: dict[str, Any] | None = None,
    revalidation: dict[str, Any] | None = None,
) -> ReleaseTrustAssessment:
    system_id = str(passport.get('identity', {}).get('system_id', ''))
    release_id = str(passport.get('release', {}).get('release_id', ''))

    hard_blockers: list[str] = []
    warnings: list[str] = []

    passport_ready = passport.get('assurance', {}).get('overall_status') == 'release-ready'
    certificate_status = certificate.get('status')
    trace_ok = trace_correlation.get('correlated') is True
    no_critical_incident = not passport.get('incident', {}).get('active_critical_incident', False)
    human_approved = passport.get('human_review', {}).get('decision') == 'approved'
    gate_passed = passport.get('release_gate', {}).get('gate_status') == 'pass'
    security_passed = (
        passport.get('security', {}).get('least_privilege_status') == 'pass'
        and passport.get('security', {}).get('confused_deputy_check') == 'pass'
        and not passport.get('security', {}).get('policy_violations', [])
    )
    quality_passed = (
        passport.get('quality', {}).get('functional_status') == 'pass'
        and passport.get('quality', {}).get('safety_status') == 'pass'
        and passport.get('quality', {}).get('groundedness_status') == 'pass'
        and passport.get('quality', {}).get('agent_task_success_status') == 'pass'
        and not passport.get('quality', {}).get('blocking_findings', [])
    )

    recovery_ok = True
    if incident_record:
        if revalidation is None:
            recovery_ok = False
            hard_blockers.append('incident exists without revalidation decision')
        elif revalidation.get('decision') != 'RESTORE':
            recovery_ok = False
            hard_blockers.append(f"recovery decision is {revalidation.get('decision', 'missing')}")

    if certificate_status == 'BLOCKED':
        hard_blockers.append('release certificate is BLOCKED')
    elif certificate_status == 'CONDITIONAL':
        warnings.append('release certificate is CONDITIONAL')
    if not trace_ok:
        hard_blockers.append('production trace does not match certified release')
    if not security_passed:
        hard_blockers.append('security controls are not passing')
    if not quality_passed:
        hard_blockers.append('quality controls are not passing')
    if not gate_passed:
        hard_blockers.append('release gate is not passing')
    if not human_approved:
        hard_blockers.append('required human approval is not satisfied')
    if not no_critical_incident:
        hard_blockers.append('active critical incident exists')

    warnings.extend(str(x) for x in passport.get('assurance', {}).get('residual_risks', []))

    factors = {
        'passport_readiness': _factor(passport_ready, 15),
        'certificate': 15 if certificate_status == 'CERTIFIED' else 8 if certificate_status == 'CONDITIONAL' else 0,
        'trace_correlation': _factor(trace_ok, 15),
        'security': _factor(security_passed, 15),
        'quality': _factor(quality_passed, 15),
        'release_gate': _factor(gate_passed, 10),
        'human_approval': _factor(human_approved, 5),
        'incident_posture': _factor(no_critical_incident, 5),
        'recovery_assurance': _factor(recovery_ok, 5),
    }
    score = min(100, sum(factors.values()))

    if hard_blockers:
        status: TrustStatus = 'BLOCKED'
    elif warnings or score < 90:
        status = 'CONDITIONAL'
    else:
        status = 'TRUSTED'

    nodes = [
        EvidenceNode(f'passport:{release_id}', 'passport', passport.get('assurance', {}).get('overall_status', 'unknown'), None),
        EvidenceNode(str(certificate.get('certificate_id', 'certificate:unknown')), 'certificate', str(certificate_status), certificate.get('integrity_sha256')),
        EvidenceNode(str(trace_correlation.get('trace_id', 'trace:unknown')), 'trace', 'correlated' if trace_ok else 'mismatch', None),
    ]
    edges = [
        EvidenceEdge(f'passport:{release_id}', str(certificate.get('certificate_id', 'certificate:unknown')), 'certified-as'),
        EvidenceEdge(str(certificate.get('certificate_id', 'certificate:unknown')), str(trace_correlation.get('trace_id', 'trace:unknown')), 'observed-in'),
    ]

    if incident_record:
        incident_id = str(incident_record.get('incident_id', 'incident:unknown'))
        nodes.append(EvidenceNode(incident_id, 'incident', str(incident_record.get('status', 'unknown')), None))
        edges.append(EvidenceEdge(str(trace_correlation.get('trace_id', 'trace:unknown')), incident_id, 'triggered'))
    if regression_asset:
        asset_id = str(regression_asset.get('asset_id', 'regression:unknown'))
        nodes.append(EvidenceNode(asset_id, 'regression_asset', 'created', regression_asset.get('integrity_sha256')))
        if incident_record:
            edges.append(EvidenceEdge(str(incident_record.get('incident_id', 'incident:unknown')), asset_id, 'generated'))
    if revalidation:
        revalidation_id = str(revalidation.get('revalidation_id', 'revalidation:unknown'))
        nodes.append(EvidenceNode(revalidation_id, 'revalidation', str(revalidation.get('decision', 'unknown')), revalidation.get('integrity_sha256')))
        if regression_asset:
            edges.append(EvidenceEdge(str(regression_asset.get('asset_id', 'regression:unknown')), revalidation_id, 'revalidated-by'))

    base = {
        'assessment_version': '1.0',
        'system_id': system_id,
        'release_id': release_id,
        'trust_score': score,
        'trust_status': status,
        'hard_blockers': sorted(set(hard_blockers)),
        'warnings': sorted(set(warnings)),
        'factors': factors,
        'nodes': [asdict(x) for x in nodes],
        'edges': [asdict(x) for x in edges],
    }
    return ReleaseTrustAssessment(
        assessment_version='1.0', system_id=system_id, release_id=release_id,
        trust_score=score, trust_status=status,
        hard_blockers=base['hard_blockers'], warnings=base['warnings'], factors=factors,
        nodes=nodes, edges=edges, integrity_sha256=_hash(base),
    )
