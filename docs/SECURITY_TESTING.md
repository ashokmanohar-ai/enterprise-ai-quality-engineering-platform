# AI security testing

Only assess owned/authorized targets. This repository uses fictional objectives, identities, accounts, policies, and canary values.

## Defense in depth

| Tool | Use | Do not use it for |
|---|---|---|
| Promptfoo | Repeatable application-specific adversarial regression in CI | broad adaptive discovery alone |
| PyRIT | Orchestrated/adaptive and multi-turn reproduction | unaudited automated gating without triage |
| Garak | Broad, scoped probe/detector discovery | every probe on every PR |

Workflow: Garak discovers → PyRIT explores/reproduces → human confirms → fix → Promptfoo permanent regression.

PyRIT's active repository is `microsoft/PyRIT`; `Azure/PyRIT` is an archived move notice. PyRIT 1.0 uses executor-oriented attack APIs. The included `PromptSendingAttack` is a safe minimal example; adaptive campaigns belong in protected environments.

Garak 0.16 prefers `--spec`. PR uses narrow injection/encoding smoke; nightly uses scoped OWASP-tagged probes; a full scan is manual/scheduled. Garak does not provide an enterprise severity for every hit, so normalization applies the documented internal mapping and records that it did so.

Promptfoo current red-team flow uses `redteam run`, with current plugin identifiers in the config. Limit tests/message size/concurrency and use a separate evaluator deployment.

## Authorization checklist

- written target-owner permission and target inventory;
- time window, rate, concurrency, max requests, cost ceiling;
- contacts, stop conditions, incident handling;
- synthetic data and explicit prohibited data classes;
- private raw evidence and retention/deletion rules;
- approval before any multi-turn/adaptive or denial-of-service-like scenario.

Set `AIQ_SECURITY_AUTHORIZED=true` only after approval. Never publish raw security artifacts from a public repository.
