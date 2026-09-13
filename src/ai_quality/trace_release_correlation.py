from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class TraceReleaseCorrelation:
    trace_id: str
    system_id: str
    release_id: str
    certificate_id: str
    certificate_status: str
    commit_sha: str
    model_version: str | None
    prompt_version: str | None
    retriever_version: str | None
    agent_version: str | None
    policy_version: str | None
    correlated: bool
    mismatches: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_runtime_trace(
    *,
    trace_id: str,
    certificate: dict[str, Any],
) -> dict[str, Any]:
    components = certificate.get('component_summary', {})
    provenance = certificate.get('provenance', {})
    return {
        'trace_id': trace_id,
        'system_id': certificate.get('system_id'),
        'release_id': certificate.get('release_id'),
        'certificate_id': certificate.get('certificate_id'),
        'certificate_status': certificate.get('status'),
        'commit_sha': certificate.get('commit_sha'),
        'component_versions': {
            'model_version': components.get('model_version'),
            'prompt_version': components.get('prompt_version'),
            'retriever_version': components.get('retriever_version'),
            'agent_version': components.get('agent_version'),
            'policy_version': provenance.get('policy_version'),
        },
        'release_provenance': {
            'certificate_integrity_sha256': certificate.get('integrity_sha256'),
            'source_bundle_id': provenance.get('source_bundle_id'),
            'source_bundle_integrity_sha256': provenance.get('source_bundle_integrity_sha256'),
        },
    }


def correlate_trace(
    trace: dict[str, Any],
    certificate: dict[str, Any],
) -> TraceReleaseCorrelation:
    components = certificate.get('component_summary', {})
    provenance = certificate.get('provenance', {})
    trace_components = trace.get('component_versions', {})

    expected = {
        'system_id': certificate.get('system_id'),
        'release_id': certificate.get('release_id'),
        'certificate_id': certificate.get('certificate_id'),
        'commit_sha': certificate.get('commit_sha'),
        'model_version': components.get('model_version'),
        'prompt_version': components.get('prompt_version'),
        'retriever_version': components.get('retriever_version'),
        'agent_version': components.get('agent_version'),
        'policy_version': provenance.get('policy_version'),
    }
    actual = {
        'system_id': trace.get('system_id'),
        'release_id': trace.get('release_id'),
        'certificate_id': trace.get('certificate_id'),
        'commit_sha': trace.get('commit_sha'),
        'model_version': trace_components.get('model_version'),
        'prompt_version': trace_components.get('prompt_version'),
        'retriever_version': trace_components.get('retriever_version'),
        'agent_version': trace_components.get('agent_version'),
        'policy_version': trace_components.get('policy_version'),
    }

    mismatches = [
        f'{field}: expected={expected[field]!r}, actual={actual[field]!r}'
        for field in expected
        if expected[field] != actual[field]
    ]

    return TraceReleaseCorrelation(
        trace_id=str(trace.get('trace_id', '')),
        system_id=str(trace.get('system_id', '')),
        release_id=str(trace.get('release_id', '')),
        certificate_id=str(trace.get('certificate_id', '')),
        certificate_status=str(trace.get('certificate_status', '')),
        commit_sha=str(trace.get('commit_sha', '')),
        model_version=trace_components.get('model_version'),
        prompt_version=trace_components.get('prompt_version'),
        retriever_version=trace_components.get('retriever_version'),
        agent_version=trace_components.get('agent_version'),
        policy_version=trace_components.get('policy_version'),
        correlated=not mismatches,
        mismatches=mismatches,
    )
