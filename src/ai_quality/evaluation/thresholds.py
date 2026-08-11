from __future__ import annotations

from typing import Any

from ai_quality.config import load_yaml


def profile_rules(profile: str) -> dict[str, Any]:
    profiles = load_yaml("config/quality-gates.yaml")["profiles"]
    selected = dict(profiles[profile])
    if "extends" not in selected:
        return selected
    parent = dict(profiles[selected.pop("extends")])
    for key, value in selected.items():
        if isinstance(value, dict) and isinstance(parent.get(key), dict):
            parent[key] = {**parent[key], **value}
        else:
            parent[key] = value
    return parent


def quality_threshold(metric: str, profile: str, default: float) -> float:
    rule = profile_rules(profile).get("quality", {}).get(metric, {})
    return float(rule.get("min", default))
