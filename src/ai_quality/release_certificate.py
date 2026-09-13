from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from hashlib import sha256
from typing import Any, Literal

from ai_quality.release_evidence_bundle import ReleaseEvidenceBundle

CertificateStatus = Literal['CERTIFIED', 'CONDITIONAL', 'BLOCKED']


@dataclass(frozen=True)
class ReleaseCertificate:
    certificate_version: str
    certificate_id: str
    issued_at: str
    status: CertificateStatus
    system_id: str
    release_id: str
    commit_sha: str
    component_summary: dict[str, Any]
    controls: dict[str, Any]
    human_approval: dict[str, Any]
    residual_risks: list[str]
    provenance: dict[str, Any]
    integrity_sha256: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _canonical_json(value: dict[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True)


def _sha256(value: dict[str, Any]) -> str:
    return sha256(_canonical_json(value).encode('utf-8')).hexdigest()


def _status(bundle: ReleaseEvidenceBundle) -> CertificateStatus:
    recommendation = bundle.release_recommendation
    passport_status = bundle.passport_decision.get('status')
    if recommendation == 'block' or passport_status in {'blocked', 'rolled-back'}:
        return 'BLOCKED'
    if recommendation in {'review-required', 'promote-with-monitoring'} or passport_status == 'conditional':
        return 'CONDITIONAL'
    return 'CERTIFIED'


def build_release_certificate(
    bundle: ReleaseEvidenceBundle,
    candidate_passport: dict[str, Any],
) -> ReleaseCertificate:
    components = candidate_passport.get('components', {})
    rag = components.get('rag', {})
    prompt = components.get('prompt', {})
    model = components.get('model', {})
    agent = components.get('agent', {})

    component_summary = {
        'dataset_id': components.get('data', {}).get('dataset_id'),
        'retriever_version': rag.get('retriever_version'),
        'index_version': rag.get('index_version'),
        'prompt_version': prompt.get('prompt_version'),
        'model_version': model.get('model_version'),
        'agent_version': agent.get('agent_version'),
        'mcp_servers': agent.get('mcp_servers', []),
        'tool_policy_version': agent.get('tool_policy_version'),
    }

    controls = {
        'passport_decision': bundle.passport_decision,
        'release_comparison': {
            'recommendation': bundle.release_comparison.get('recommendation'),
            'risk_level': bundle.release_comparison.get('risk_level'),
            'new_blockers': bundle.release_comparison.get('new_blockers', []),
        },
        'release_gate': candidate_passport.get('release_gate', {}),
        'security': candidate_passport.get('security', {}),
        'quality': candidate_passport.get('quality', {}),
        'incident': candidate_passport.get('incident', {}),
    }

    residual_risks = list(candidate_passport.get('assurance', {}).get('residual_risks', []))
    residual_risks.extend(bundle.passport_decision.get('warnings', []))
    residual_risks = sorted(set(residual_risks))

    provenance = {
        'source_bundle_id': bundle.bundle_id,
        'source_bundle_integrity_sha256': bundle.integrity_sha256,
        'evidence_refs': bundle.evidence_refs,
        'rollback_plan': bundle.rollback_plan,
        'policy_version': candidate_passport.get('release_gate', {}).get('policy_version'),
    }

    base_payload: dict[str, Any] = {
        'certificate_version': '1.0',
        'certificate_id': f"cert-{bundle.release_id}",
        'issued_at': datetime.now(UTC).isoformat(),
        'status': _status(bundle),
        'system_id': bundle.system_id,
        'release_id': bundle.release_id,
        'commit_sha': bundle.commit_sha,
        'component_summary': component_summary,
        'controls': controls,
        'human_approval': bundle.human_approval,
        'residual_risks': residual_risks,
        'provenance': provenance,
    }
    return ReleaseCertificate(**base_payload, integrity_sha256=_sha256(base_payload))


def render_markdown(certificate: ReleaseCertificate) -> str:
    data = certificate.to_dict()
    components = data['component_summary']
    return '\n'.join([
        f"# AI Release Certificate — {data['release_id']}",
        '',
        f"**Status:** {data['status']}",
        f"**System:** {data['system_id']}",
        f"**Release:** {data['release_id']}",
        f"**Commit:** `{data['commit_sha']}`",
        f"**Certificate ID:** `{data['certificate_id']}`",
        f"**Issued:** {data['issued_at']}",
        '',
        '## Component versions',
        '',
        f"- Dataset: `{components.get('dataset_id')}`",
        f"- Retriever: `{components.get('retriever_version')}`",
        f"- Index: `{components.get('index_version')}`",
        f"- Prompt: `{components.get('prompt_version')}`",
        f"- Model: `{components.get('model_version')}`",
        f"- Agent: `{components.get('agent_version')}`",
        f"- MCP servers: `{', '.join(components.get('mcp_servers', []))}`",
        f"- Tool policy: `{components.get('tool_policy_version')}`",
        '',
        '## Release controls',
        '',
        f"- Passport decision: **{data['controls']['passport_decision'].get('status')}**",
        f"- Comparison recommendation: **{data['controls']['release_comparison'].get('recommendation')}**",
        f"- Risk level: **{data['controls']['release_comparison'].get('risk_level')}**",
        f"- Human approval: **{data['human_approval'].get('decision')}**",
        f"- Release gate: **{data['controls']['release_gate'].get('gate_status')}**",
        '',
        '## Residual risks',
        '',
        *(f"- {risk}" for risk in data['residual_risks']),
        '',
        '## Provenance attestation',
        '',
        f"- Evidence bundle: `{data['provenance']['source_bundle_id']}`",
        f"- Bundle SHA-256: `{data['provenance']['source_bundle_integrity_sha256']}`",
        f"- Certificate SHA-256: `{data['integrity_sha256']}`",
        f"- Policy version: `{data['provenance'].get('policy_version')}`",
        '',
        '> This certificate summarizes deterministic release-assurance evidence. It is not a cryptographic signature or legal certification.',
        '',
    ])
