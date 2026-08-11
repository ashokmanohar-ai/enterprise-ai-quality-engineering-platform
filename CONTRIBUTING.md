# Contributing

1. Create a focused branch and do not commit `.env` or raw reports.
2. Add or update a canonical dataset case for behavior changes.
3. Run `make validate` and `make test-pr`.
4. If an adapter changes, retain the native result under `reports/raw` only during the run and verify its normalized contract.
5. Explain threshold, security severity, cost, and compatibility changes in the pull request.
6. Never weaken a blocking rule merely to make CI green; calibrate it with evidence and review.
