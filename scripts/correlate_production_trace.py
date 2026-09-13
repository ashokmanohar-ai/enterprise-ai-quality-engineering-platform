from __future__ import annotations

import argparse
import json
from pathlib import Path

from ai_quality.release_certificate import build_release_certificate
from ai_quality.release_evidence_bundle import build_release_evidence_bundle
from ai_quality.trace_release_correlation import build_runtime_trace, correlate_trace


def main() -> int:
    parser = argparse.ArgumentParser(description='Correlate a production trace with an AI release certificate.')
    parser.add_argument('--baseline', required=True)
    parser.add_argument('--candidate', required=True)
    parser.add_argument('--trace-id', default='trace-demo-001')
    parser.add_argument('--trace-out', default='reports/production-trace.json')
    parser.add_argument('--correlation-out', default='reports/trace-release-correlation.json')
    args = parser.parse_args()

    baseline = json.loads(Path(args.baseline).read_text(encoding='utf-8'))
    candidate = json.loads(Path(args.candidate).read_text(encoding='utf-8'))

    bundle = build_release_evidence_bundle(baseline, candidate)
    certificate = build_release_certificate(bundle, candidate)
    certificate_dict = certificate.to_dict()

    trace = build_runtime_trace(trace_id=args.trace_id, certificate=certificate_dict)
    correlation = correlate_trace(trace, certificate_dict)

    trace_path = Path(args.trace_out)
    corr_path = Path(args.correlation_out)
    trace_path.parent.mkdir(parents=True, exist_ok=True)
    corr_path.parent.mkdir(parents=True, exist_ok=True)
    trace_path.write_text(json.dumps(trace, indent=2, sort_keys=True), encoding='utf-8')
    corr_path.write_text(json.dumps(correlation.to_dict(), indent=2, sort_keys=True), encoding='utf-8')

    print(f'trace_id={correlation.trace_id}')
    print(f'release_id={correlation.release_id}')
    print(f'certificate_id={correlation.certificate_id}')
    print(f'correlated={correlation.correlated}')
    if correlation.mismatches:
        for mismatch in correlation.mismatches:
            print(f'mismatch={mismatch}')
    return 0 if correlation.correlated else 2


if __name__ == '__main__':
    raise SystemExit(main())
