from __future__ import annotations

import argparse
import json
from pathlib import Path

from ai_quality.incident_revalidation_gate import evaluate_revalidation


def main() -> int:
    parser = argparse.ArgumentParser(description='Evaluate incident revalidation and recovery readiness.')
    parser.add_argument('--assurance-record', required=True)
    parser.add_argument('--regression-asset', required=True)
    parser.add_argument('--results', required=True)
    parser.add_argument('--out', default='reports/incident-revalidation-decision.json')
    args = parser.parse_args()

    assurance = json.loads(Path(args.assurance_record).read_text(encoding='utf-8'))
    regression = json.loads(Path(args.regression_asset).read_text(encoding='utf-8'))
    results = json.loads(Path(args.results).read_text(encoding='utf-8'))

    decision = evaluate_revalidation(
        assurance_record=assurance,
        regression_asset=regression,
        results=results,
    )
    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(decision.to_dict(), indent=2, sort_keys=True), encoding='utf-8')

    print(f'decision={decision.decision}')
    print(f'revalidation_id={decision.revalidation_id}')
    print(f'integrity_sha256={decision.integrity_sha256}')
    return 0 if decision.decision == 'RESTORE' else 2


if __name__ == '__main__':
    raise SystemExit(main())
