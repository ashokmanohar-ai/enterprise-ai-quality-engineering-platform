import json
from pathlib import Path


def test_inspector_config_uses_no_secrets() -> None:
    text = Path("mcp/inspector/mcp.json").read_text(encoding="utf-8")
    payload = json.loads(text)
    assert payload["servers"]["acmecloud-support"]["command"] == "python"
    assert "key" not in text.lower()
