from __future__ import annotations

import asyncio

from ai_quality.config import Settings, get_settings


async def run_prompt_sending(objective: str, settings: Settings | None = None):  # type: ignore[no-untyped-def]
    """PyRIT 1.0 executor API. Only safe synthetic objectives are accepted."""
    configured = settings or get_settings()
    if not configured.aiq_security_authorized:
        raise PermissionError("Set AIQ_SECURITY_AUTHORIZED=true only for an authorized target.")
    forbidden = ("real password", "production credential", "customer data")
    if any(term in objective.lower() for term in forbidden):
        raise ValueError("Only synthetic red-team objectives are allowed.")
    configured.require_azure()
    try:
        from pyrit.executor.attack import PromptSendingAttack
        from pyrit.prompt_target import OpenAIChatTarget
        from pyrit.setup import IN_MEMORY, initialize_pyrit_async
    except ImportError as exc:
        raise RuntimeError("Install PyRIT with: pip install -e '.[security-pyrit]'") from exc
    await initialize_pyrit_async(memory_db_type=IN_MEMORY)
    assert (
        configured.azure_openai_api_key
        and configured.azure_openai_endpoint
        and configured.azure_openai_chat_deployment
    )
    endpoint = f"{configured.azure_openai_endpoint.rstrip('/')}/openai/v1"
    target = OpenAIChatTarget(
        model_name=configured.azure_openai_chat_deployment,
        endpoint=endpoint,
        api_key=configured.azure_openai_api_key.get_secret_value(),
    )
    attack = PromptSendingAttack(objective_target=target)
    return await attack.execute_async(objective=objective)


def run(objective: str):  # type: ignore[no-untyped-def]
    return asyncio.run(run_prompt_sending(objective))
