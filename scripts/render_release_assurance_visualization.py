from __future__ import annotations

import argparse
import json
from pathlib import Path

from ai_quality.incident_regression_loop import build_incident_assurance_record, build_regression_asset
from ai_quality.incident_revalidation_gate import evaluate_revalidation
from ai_quality.release_assurance_visualization import build_timeline, render_release_assurance_html
from ai_quality.release_certificate import build_release_certificate
from ai_quality.release_evidence_bundle import build_release_evidence_bundle
from ai_quality.release_trust_graph import build_release_trust_assessment
from ai_quality.trace_release_correlation import build_runtime_trace, correlate_trace


def main() -> int:
    parser = argparse.ArgumentParser(description='Render release assurance timeline and evidence graph.')
    parser.add_argument('--baseline', required=True)
    parser.add_argument('--candidate', required=True)
    parser.add_argument('--incident', required=True)
    parser.add_argument('--revalidation', required=True)
    parser.add_argument('--trace-id', default='trace-prod-demo-001')
    parser.add_argument('--html-out', default='reports/release-assurance-timeline.html')
    parser.add_argument('--json-out', default='reports/release-assurance-timeline.json')
    args = parser.parse_args()

    baseline = json.loads(Path(args.baseline).read_text(encoding='utf-8'))
    candidate = json.loads(Path(args.candidate).read_text(encoding='utf-8'))
    incident = json.loads(Path(args.incident).read_text(encoding='utf-8'))
    results = json.loads(Path(args.revalidation).read_text(encoding='utf-8'))

    bundle = build_release_evidence_bundle(baseline, candidate)
    certificate = build_release_certificate(bundle, candidate)
    trace = build_runtime_trace(trace_id=args.trace_id, certificate=certificate.to_dict())
    correlation = correlate_trace(trace, certificate.to_dict())
    asset = build_regression_asset(
        incident=incident,
        trace=trace,
        correlation=correlation.to_dict(),
        certificate=certificate.to_dict(),
    )
    record = build_incident_assurance_record(
        incident=incident,
        trace=trace,
        correlation=correlation.to_dict(),
        certificate=certificate.to_dict(),
    )
    revalidation = evaluate_revalidation(
        assurance_record=record,
        regression_asset=asset.to_dict(),
        results=results,
    )
    assessment = build_release_trust_assessment(
        passport=candidate,
        certificate=certificate.to_dict(),
        trace_correlation=correlation.to_dict(),
        incident_record=record,
        regression_asset=asset.to_dict(),
        revalidation=revalidation.to_dict(),
    )

    html = render_release_assurance_html(
        passport=candidate,
        certificate=certificate.to_dict(),
        trace_correlation=correlation.to_dict(),
        incident_record=record,
        regression_asset=asset.to_dict(),
        revalidation=revalidation.to_dict(),
        trust_assessment=assessment.to_dict(),
    )
    timeline = build_timeline(
        passport=candidate,
        certificate=certificate.to_dict(),
        trace_correlation=correlation.to_dict(),
        incident_record=record,
        regression_asset=asset.to_dict(),
        revalidation=revalidation.to_dict(),
        trust_assessment=assessment.to_dict(),
    )

    html_path = Path(args.html_out)
    json_path = Path(args.json_out)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(html, encoding='utf-8')
    json_path.write_text(json.dumps({
        'system_id': assessment.system_id,
        'release_id': assessment.release_id,
        'trust_status': assessment.trust_status,
        'trust_score': assessment.trust_score,
        'timeline': timeline,
        'nodes': [node.__dict__ for node in assessment.nodes],
        'edges': [edge.__dict__ for edge in assessment.edges],
    }, indent=2, sort_keys=True), encoding='utf-8')

    print(f'trust_status={assessment.trust_status}')
    print(f'trust_score={assessment.trust_score}')
    print(f'timeline_stages={len(timeline)}')
    print(f'graph_nodes={len(assessment.nodes)}')
    print(f'graph_edges={len(assessment.edges)}')
    return 0 if assessment.trust_status != 'BLOCKED' else 2


if __name__ == '__main__':
    raise SystemExit(main())
