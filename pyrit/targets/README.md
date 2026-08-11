# PyRIT targets

The maintained target is PyRIT 1.0.1 `OpenAIChatTarget`, configured from the shared Azure environment. No endpoint, key, or deployment is committed. For application-layer testing, subclass `PromptChatTarget` and route requests through the same `ApplicationUnderTest` contract rather than attacking a raw model.
