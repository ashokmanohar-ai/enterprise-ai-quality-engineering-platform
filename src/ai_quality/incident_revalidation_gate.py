from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from typing import Any, Literal

RecoveryDecision = Literal['RESTORE', 'HOLD', 'ROLLBACK']


@dataclass(frozen=True)
class RevalidationDecision:
    decision_version: str
    revalidation_id: str
    incident_id: str
    regression_asset_id: str
    release_id: str
    decision: RecoveryDecision
    mandatory_checks: dict[str, str]
    blockers: list[str]
    warnings: list[str]
    evidence_refs: list[str]
    integrity_sha256: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _canonical_json(value: dict[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _hash(value: dict[str, Any]) -> str:
    return sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def evaluate_revalidation(
    *,
    assurance_record: dict[str, Any],
    regression_asset: dict[str, Any],
    results: dict[str, Any],
) -> RevalidationDecision:
    incident_id = str(assurance_record.get('incident_id', ''))
    release_id = str(assurance_record.get('release_id', regression_asset.get('release_id', '')))
    asset_id = str(regression_asset.get('asset_id', assurance_record.get('regression_asset_id', '')))
    revalidation_id = str(results.get('revalidation_id') or f'revalidate-{incident_id}')

    checks = {
        'incident_reproduction': str(results.get('incident_reproduction', 'missing')),
        'targeted_regression': str(results.get('targeted_regression', 'missing')),
        'safety_regression': str(results.get('safety_regression', 'missing')),
        'authorization_regression': str(results.get('authorization_regression', 'missing')),
        'trace_correlation': 'pass' if assurance_record.get('trace_correlated') else 'fail',
        'certificate_status': 'pass' if assurance_record.get('certificate_status') in {'CERTIFIED', 'CONDITIONAL'} else 'fail',
        'root_cause_fix_verified': str(results.get('root_cause_fix_verified', 'missing')),
        'rollback_readiness': str(results.get('rollback_readiness', 'missing')),
        'human_approval': str(results.get('human_approval', 'missing')),
    }

    blockers: list[str] = []
    warnings: list[str] = []
    mandatory = {
        'incident_reproduction', 'targeted_regression', 'safety_regression',
        'authorization_regression', 'trace_correlation', 'root_cause_fix_verified',
        'rollback_readiness', 'human_approval',
    }
    for name in mandatory:
        status = checks[name]
        if status == 'fail':
            blockers.append(f'{name} failed')
        elif status != 'pass':
            blockers.append(f'{name} is {status}')

    if checks['certificate_status'] != 'pass':
        blockers.append('release certificate is not eligible for recovery')

    residual = results.get('residual_risks', [])
    if residual:
        warnings.extend(str(item) for item in residual)

    if results.get('rollback_required') is True:
        decision: RecoveryDecision = 'ROLLBACK'
    elif blockers:
        decision = 'HOLD'
    else:
        decision = 'RESTORE'

    evidence_refs = sorted(set(
        list(results.get('evidence_refs', []))
        + list(regression_asset.get('root_cause', {}).get('evidence_refs', []))
        + [f"evidence://regression/{asset_id}"]
    ))

    base = {
        'decision_version': '1.0',
        'revalidation_id': revalidation_id,
        'incident_id': incident_id,
        'regression_asset_id': asset_id,
        'release_id': release_id,
        'decision': decision,
        'mandatory_checks': checks,
        'blockers': blockers,
        'warnings': warnings,
        'evidence_refs': evidence_refs,
    }
    return RevalidationDecision(**base, integrity_sha256=_hash(base))
