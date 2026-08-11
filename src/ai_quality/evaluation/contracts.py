from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Severity(StrEnum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ExpectedBehavior(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    must_include: list[str] = Field(default_factory=list)
    must_not_claim: list[str] = Field(default_factory=list)
    expected_tools: list[str] = Field(default_factory=list)
    forbidden_tools: list[str] = Field(default_factory=list)
    max_tool_calls: int | None = Field(default=None, ge=0)
    output_schema: dict[str, Any] | None = Field(default=None, alias="schema")


class CanonicalCase(BaseModel):
    id: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]+$")
    category: Literal["functional", "rag", "agent", "mcp", "security", "structured"]
    input: str
    reference_answer: str | None = None
    contexts: list[str] = Field(default_factory=list)
    expected_behavior: ExpectedBehavior = Field(default_factory=ExpectedBehavior)
    tags: list[str] = Field(default_factory=list)
    critical: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def rag_requires_context(self) -> CanonicalCase:
        if self.category == "rag" and not self.contexts:
            raise ValueError("RAG cases require at least one reference context")
        return self


class EvaluationResult(BaseModel):
    test_id: str
    framework: str
    category: str
    metric: str
    score: float | None = Field(default=None, ge=0, le=1)
    threshold: float | None = Field(default=None, ge=0, le=1)
    passed: bool
    reason: str = ""
    latency_ms: float | None = Field(default=None, ge=0)
    token_usage: dict[str, int] = Field(default_factory=dict)
    trace_id: str | None = None
    severity: Severity | None = None
    blocking: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class SecurityFinding(BaseModel):
    id: str
    framework: Literal["promptfoo", "pyrit", "garak", "custom"]
    category: str
    severity: Severity | None = None
    input: str
    result: str
    reproducible: bool = False
    blocking: bool = False
    source_severity: str | None = None
    internal_mapping_applied: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class PerformanceResult(BaseModel):
    scenario: str
    metric: str
    value: float
    unit: str
    threshold: float | None = None
    comparison: Literal["min", "max"] | None = None
    passed: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)


class RunMetadata(BaseModel):
    evaluation_run_id: str
    experiment_id: str | None = None
    git_commit: str = "unknown"
    branch: str = "unknown"
    dataset_version: str
    prompt_version: str
    model_deployment: str | None = None
    evaluator_deployment: str | None = None
    embedding_deployment: str | None = None
    retriever_settings: dict[str, Any] = Field(default_factory=dict)
    tool_versions: dict[str, str] = Field(default_factory=dict)
    random_seed: int = 42
    threshold_config: str = "config/quality-gates.yaml"
    environment: str = "local"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class QualityReport(BaseModel):
    status: Literal["PASS", "FAIL"]
    profile: str
    summary: dict[str, Literal["PASS", "FAIL", "SKIP"]]
    blocking_failures: list[EvaluationResult] = Field(default_factory=list)
    results: list[EvaluationResult] = Field(default_factory=list)
    security_findings: list[SecurityFinding] = Field(default_factory=list)
    performance_results: list[PerformanceResult] = Field(default_factory=list)
    regressions: list[dict[str, Any]] = Field(default_factory=list)
    metadata: RunMetadata
