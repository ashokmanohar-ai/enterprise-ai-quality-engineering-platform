from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from typing import Any


@dataclass(frozen=True)
class RegressionAsset:
    asset_version: str
    asset_id: str
    incident_id: str
    trace_id: str
    certificate_id: str
    release_id: str
    root_cause: dict[str, Any]
    reproduction: dict[str, Any]
    expected_behavior: dict[str, Any]
    regression_scope: list[str]
    provenance: dict[str, Any]
    integrity_sha256: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _canonical_json(value: dict[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _hash(value: dict[str, Any]) -> str:
    return sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def build_regression_asset(
    *,
    incident: dict[str, Any],
    trace: dict[str, Any],
    correlation: dict[str, Any],
    certificate: dict[str, Any],
) -> RegressionAsset:
    incident_id = str(incident.get("incident_id", ""))
    trace_id = str(trace.get("trace_id", ""))
    certificate_id = str(correlation.get("certificate_id", certificate.get("certificate_id", "")))
    release_id = str(correlation.get("release_id", certificate.get("release_id", "")))

    root_cause = {
        "category": incident.get("root_cause", {}).get("category"),
        "component": incident.get("root_cause", {}).get("component"),
        "summary": incident.get("root_cause", {}).get("summary"),
        "evidence_refs": incident.get("root_cause", {}).get("evidence_refs", []),
    }

    reproduction = {
        "input_ref": incident.get("reproduction", {}).get("input_ref"),
        "preconditions": incident.get("reproduction", {}).get("preconditions", []),
        "tool_sequence": incident.get("reproduction", {}).get("tool_sequence", []),
        "observed_behavior": incident.get("reproduction", {}).get("observed_behavior"),
    }

    expected_behavior = {
        "expected_result": incident.get("expected_behavior", {}).get("expected_result"),
        "blocking_assertions": incident.get("expected_behavior", {}).get("blocking_assertions", []),
    }

    scope = sorted(set(
        incident.get("regression_scope", [])
        or [value for value in [root_cause.get("component")] if value]
    ))

    provenance = {
        "trace_correlation_valid": correlation.get("correlated", False),
        "trace_mismatches": correlation.get("mismatches", []),
        "certificate_status": certificate.get("status"),
        "certificate_integrity_sha256": certificate.get("integrity_sha256"),
        "source_bundle_id": certificate.get("provenance", {}).get("source_bundle_id"),
        "source_bundle_integrity_sha256": certificate.get("provenance", {}).get("source_bundle_integrity_sha256"),
    }

    base = {
        "asset_version": "1.0",
        "asset_id": f"regression-{incident_id}",
        "incident_id": incident_id,
        "trace_id": trace_id,
        "certificate_id": certificate_id,
        "release_id": release_id,
        "root_cause": root_cause,
        "reproduction": reproduction,
        "expected_behavior": expected_behavior,
        "regression_scope": scope,
        "provenance": provenance,
    }
    return RegressionAsset(**base, integrity_sha256=_hash(base))


def build_incident_assurance_record(
    *,
    incident: dict[str, Any],
    trace: dict[str, Any],
    correlation: dict[str, Any],
    certificate: dict[str, Any],
) -> dict[str, Any]:
    asset = build_regression_asset(
        incident=incident,
        trace=trace,
        correlation=correlation,
        certificate=certificate,
    )
    return {
        "incident_id": incident.get("incident_id"),
        "severity": incident.get("severity"),
        "status": incident.get("status"),
        "trace_id": trace.get("trace_id"),
        "release_id": correlation.get("release_id"),
        "certificate_id": correlation.get("certificate_id"),
        "certificate_status": correlation.get("certificate_status"),
        "trace_correlated": correlation.get("correlated", False),
        "root_cause": asset.root_cause,
        "regression_asset_id": asset.asset_id,
        "regression_asset_integrity_sha256": asset.integrity_sha256,
        "release_action": incident.get("release_action", "hold-and-revalidate"),
    }
