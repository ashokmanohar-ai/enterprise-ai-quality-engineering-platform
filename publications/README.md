# Technical White Papers

This directory is the publication index for technical white papers associated with the **Enterprise AI Quality Engineering Platform** and authored by **Ashok Kumar Manohar**.

## 1. Testing MCP-Powered AI Agents

**Testing MCP-Powered AI Agents: Security, Authorization and Quality Engineering Patterns for Enterprise Tool-Connected AI**

- [Read the white paper](../WHITEPAPER.md)
- [Citation metadata](../CITATION.cff)
- Version: 1.0
- Published: September 2026

Focus: MCP protocol and contract testing, authentication, authorization, scope escalation, tool risk classification, business rules, agent tool selection, trajectories, human approval, prompt injection, tool poisoning, tenant isolation, observability and CI/CD quality gates.

---

## 2. Agentic AI Security Testing

**Agentic AI Security Testing: Prompt Injection, Tool Abuse, Excessive Agency and Data Leakage**

- [Read the white paper](AGENTIC_AI_SECURITY_TESTING.md)
- [Citation metadata](CITATION_AGENTIC_AI_SECURITY_TESTING.cff)
- Version: 1.0
- Published: September 2026

Focus: direct and indirect prompt injection, excessive agency, tool abuse, identity and authorization, scope escalation, data leakage, cross-tenant isolation, memory and tool poisoning, MCP security, human approval, repeated side effects, resource exhaustion, adversarial discovery, permanent security regression, observability and CI/CD security gates.

---

## 3. Enterprise AI Quality Engineering — Reference Architecture

**Enterprise AI Quality Engineering: A Reference Architecture for Testing LLM, RAG, Agentic AI and MCP Systems**

- [Read the white paper](ENTERPRISE_AI_QUALITY_ENGINEERING_REFERENCE_ARCHITECTURE.md)
- [Citation metadata](CITATION_ENTERPRISE_AI_QE_REFERENCE_ARCHITECTURE.cff)
- Version: 1.0
- Published: September 2026

Focus: enterprise AI Quality Control Plane, explicit quality contracts, deterministic-first controls, LLM/RAG/agent/MCP/prompt/embedding evaluation, authoritative identity and authorization, AI security, HITL approval, observability, normalized evidence, baseline comparison, risk-based CI/CD profiles, unified release gates and production-to-regression learning.

> **Flagship architecture paper:** this publication connects the repository's specialist evaluation and security capabilities into one enterprise operating model for evidence-backed AI release decisions.

---

## Reference Implementation

All three publications are supported by the open-source [Enterprise AI Quality Engineering Platform](https://github.com/ashokmanohar-ai/enterprise-ai-quality-engineering-platform), which combines LLM, RAG, agent, MCP, prompt, security, embedding, performance and observability testing under one normalized quality-gate model.

The reference architecture assigns primary ownership to specialist tools rather than forcing every framework to test every concern. It uses canonical datasets, normalized evidence, baseline comparison and hard release gates so critical authorization, security or missing-evidence failures cannot disappear inside aggregate scores.

Security testing in the reference implementation separates broad discovery, controlled reproduction and durable regression. The documented pattern is **Garak discovery → PyRIT exploration/reproduction → human confirmation → Promptfoo permanent regression**, with security profiles requiring explicit authorization before execution.

> These are independent technical white papers and are not peer-reviewed academic publications, penetration-test authorizations, compliance certifications, security certifications, or statements of production readiness.