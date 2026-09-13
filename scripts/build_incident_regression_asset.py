from __future__ import annotations

import argparse
import json
from pathlib import Path

from ai_quality.incident_regression_loop import build_incident_assurance_record, build_regression_asset
from ai_quality.release_certificate import build_release_certificate
from ai_quality.release_evidence_bundle import build_release_evidence_bundle
from ai_quality.trace_release_correlation import build_runtime_trace, correlate_trace


def main() -> int:
    parser = argparse.ArgumentParser(description='Convert a production incident into a regression asset.')
    parser.add_argument('--baseline', required=True)
    parser.add_argument('--candidate', required=True)
    parser.add_argument('--incident', required=True)
    parser.add_argument('--trace-id', required=True)
    parser.add_argument('--asset-out', default='reports/incident-regression-asset.json')
    parser.add_argument('--record-out', default='reports/incident-assurance-record.json')
    args = parser.parse_args()

    baseline = json.loads(Path(args.baseline).read_text(encoding='utf-8'))
    candidate = json.loads(Path(args.candidate).read_text(encoding='utf-8'))
    incident = json.loads(Path(args.incident).read_text(encoding='utf-8'))

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

    asset_path = Path(args.asset_out)
    record_path = Path(args.record_out)
    asset_path.parent.mkdir(parents=True, exist_ok=True)
    record_path.parent.mkdir(parents=True, exist_ok=True)
    asset_path.write_text(json.dumps(asset.to_dict(), indent=2, sort_keys=True), encoding='utf-8')
    record_path.write_text(json.dumps(record, indent=2, sort_keys=True), encoding='utf-8')

    print(f"incident_id={asset.incident_id}")
    print(f"regression_asset_id={asset.asset_id}")
    print(f"trace_correlated={correlation.correlated}")
    print(f"release_action={record['release_action']}")
    return 0 if correlation.correlated else 2


if __name__ == '__main__':
    raise SystemExit(main())
