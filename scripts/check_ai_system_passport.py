from __future__ import annotations

import json
import sys
from pathlib import Path

from ai_quality.passport_engine import evaluate_passport


def main() -> int:
    path = Path(sys.argv[1] if len(sys.argv) > 1 else 'examples/ai-system-passport.example.json')
    passport = json.loads(path.read_text(encoding='utf-8'))
    decision = evaluate_passport(passport)
    output = {
        'passport': str(path),
        'status': decision.status,
        'blocking_reasons': list(decision.reasons),
        'warnings': list(decision.warnings),
    }
    print(json.dumps(output, indent=2))
    return 1 if decision.status in {'blocked', 'rolled-back'} else 0


if __name__ == '__main__':
    raise SystemExit(main())
