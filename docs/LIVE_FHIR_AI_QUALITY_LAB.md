# Live FHIR AI Quality Lab

**Live demo:** https://fhir-ai-quality-lab.vercel.app  
**Portfolio case study:** https://ashok-kumar-manohar-portfolio.vercel.app/case-studies/fhir-ai-quality-lab

## What is real in the live demo

The public application includes a same-origin Vercel API route that performs a real request to the public HAPI FHIR R4 test server. A successful run returns real HTTP status, a Patient resource identifier and measured server latency.

```text
Browser → Vercel API → public HAPI FHIR R4 → Patient search/read → evidence
```

## What remains synthetic

AI groundedness, tool quality, PHI-safety and release-readiness scenarios use deterministic synthetic evidence so the public demo stays credential-free, reproducible and safe. These values are explicitly labelled as synthetic in the UI.

## How this repository relates

This repository provides the broader enterprise AI-quality engineering proof behind the demo: canonical datasets, LLM/RAG/agent/MCP evaluation, DeepEval, Ragas, Promptfoo, security profiles, performance checks, observability and hard release gates.

Production healthcare deployment would additionally require authenticated SMART/OAuth flows, formal FHIR profile and terminology validation, governed persistence, environment-specific authorization, healthcare security/compliance controls and production observability.

## Recruiter route

1. Run **Live FHIR Check** in the demo.
2. Inspect HTTP status, Patient ID and latency.
3. Review the portfolio case study for the architecture and limitations.
4. Return here to inspect the evaluation contracts, security controls, MCP tests, observability and quality-gate implementation.
