from __future__ import annotations

import argparse
import json
from pathlib import Path

from ai_quality.release_certificate import build_release_certificate, render_markdown
from ai_quality.release_evidence_bundle import build_release_evidence_bundle


def main() -> int:
    parser = argparse.ArgumentParser(description='Build AI release certificate and provenance attestation.')
    parser.add_argument('--baseline', required=True)
    parser.add_argument('--candidate', required=True)
    parser.add_argument('--json-out', default='reports/release-certificate.json')
    parser.add_argument('--md-out', default='reports/release-certificate.md')
    args = parser.parse_args()

    baseline = json.loads(Path(args.baseline).read_text(encoding='utf-8'))
    candidate = json.loads(Path(args.candidate).read_text(encoding='utf-8'))

    bundle = build_release_evidence_bundle(baseline, candidate)
    certificate = build_release_certificate(bundle, candidate)

    json_path = Path(args.json_out)
    md_path = Path(args.md_out)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(certificate.to_dict(), indent=2, sort_keys=True), encoding='utf-8')
    md_path.write_text(render_markdown(certificate), encoding='utf-8')

    print(f"status={certificate.status}")
    print(f"certificate_id={certificate.certificate_id}")
    print(f"integrity_sha256={certificate.integrity_sha256}")
    return 0 if certificate.status != 'BLOCKED' else 2


if __name__ == '__main__':
    raise SystemExit(main())
