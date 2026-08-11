from __future__ import annotations

from pathlib import Path

from ai_quality.config import ROOT


def load_policy_documents(
    path: str | Path = "knowledge_base/policies",
) -> list[tuple[str, str, dict[str, str]]]:
    resolved = Path(path)
    if not resolved.is_absolute():
        resolved = ROOT / resolved
    documents: list[tuple[str, str, dict[str, str]]] = []
    for file in sorted(resolved.glob("*.md")):
        documents.append((file.stem, file.read_text(encoding="utf-8"), {"source": file.name}))
    if not documents:
        raise RuntimeError(f"No policy documents found in {resolved}")
    return documents
