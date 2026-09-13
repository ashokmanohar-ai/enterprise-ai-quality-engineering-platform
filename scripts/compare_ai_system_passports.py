from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from ai_quality.passport_diff import compare_passports


def main() -> int:
    parser = argparse.ArgumentParser(description='Compare baseline and candidate AI System Passports.')
    parser.add_argument('baseline', type=Path)
    parser.add_argument('candidate', type=Path)
    parser.add_argument('--output', type=Path, default=Path('reports/passport-diff.json'))
    args = parser.parse_args()

    baseline = json.loads(args.baseline.read_text(encoding='utf-8'))
    candidate = json.loads(args.candidate.read_text(encoding='utf-8'))
    comparison = compare_passports(baseline, candidate)

    payload = {
        'recommendation': comparison.recommendation,
        'risk_level': comparison.risk_level,
        'approval_changed': comparison.approval_changed,
        'new_blockers': comparison.new_blockers,
        'changes': [asdict(change) for change in comparison.changes],
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding='utf-8')
    print(json.dumps(payload, indent=2))

    return 1 if comparison.recommendation == 'block' else 0


if __name__ == '__main__':
    raise SystemExit(main())
