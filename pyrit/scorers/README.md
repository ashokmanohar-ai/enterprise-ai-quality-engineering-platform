# PyRIT scorers

Use deterministic refusal/secret-canary scorers first, then a separate Azure evaluator deployment for nuanced goal-achievement scoring. A PyRIT score is normalized into `SecurityFinding`; if PyRIT does not emit severity, the internal mapping in `config/security.yaml` is applied and marked with `internal_mapping_applied=true`.
