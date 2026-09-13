from __future__ import annotations

import argparse
import json
from pathlib import Path

from ai_quality.incident_regression_loop import build_incident_assurance_record, build_regression_asset
from ai_quality.incident_revalidation_gate import evaluate_revalidation
from ai_quality.release_certificate import build_release_certificate
from ai_quality.release_evidence_bundle import build_release_evidence_bundle
from ai_quality.release_trust_graph import build_release_trust_assessment
from ai_quality.trace_release_correlation import build_runtime_trace, correlate_trace


def main() -> int:
    parser = argparse.ArgumentParser(description='Build explainable release trust score and evidence graph.')
    parser.add_argument('--baseline', required=True)
    parser.add_argument('--candidate', required=True)
    parser.add_argument('--incident', required=True)
    parser.add_argument('--revalidation', required=True)
    parser.add_argument('--trace-id', default='trace-prod-demo-001')
    parser.add_argument('--out', default='reports/release-trust-assessment.json')
    args = parser.parse_args()

    baseline = json.loads(Path(args.baseline).read_text())
    candidate = json.loads(Path(args.candidate).read_text())
    incident = json.loads(Path(args.incident).read_text())
    results = json.loads(Path(args.revalidation).read_text())

    bundle = build_release_evidence_bundle(baseline, candidate)
    certificate = build_release_certificate(bundle, candidate)
    trace = build_runtime_trace(trace_id=args.trace_id, certificate=certificate.to_dict())
    correlation = correlate_trace(trace, certificate.to_dict())
    asset = build_regression_asset(incident=incident, trace=trace, correlation=correlation.to_dict(), certificate=certificate.to_dict())
    record = build_incident_assurance_record(incident=incident, trace=trace, correlation=correlation.to_dict(), certificate=certificate.to_dict())
    revalidation = evaluate_revalidation(assurance_record=record, regression_asset=asset.to_dict(), results=results)

    assessment = build_release_trust_assessment(
        passport=candidate,
        certificate=certificate.to_dict(),
        trace_correlation=correlation.to_dict(),
        incident_record=record,
        regression_asset=asset.to_dict(),
        revalidation=revalidation.to_dict(),
    )

    path = Path(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(assessment.to_dict(), indent=2, sort_keys=True), encoding='utf-8')
    print(f'trust_status={assessment.trust_status}')
    print(f'trust_score={assessment.trust_score}')
    print(f'hard_blockers={len(assessment.hard_blockers)}')
    print(f'graph_nodes={len(assessment.nodes)}')
    print(f'graph_edges={len(assessment.edges)}')
    return 0 if assessment.trust_status != 'BLOCKED' else 2


if __name__ == '__main__':
    raise SystemExit(main())
