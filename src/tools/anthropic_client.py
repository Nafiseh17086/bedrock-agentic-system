"""Direct Anthropic API client — fallback for when AWS isn't available."""

import time
from typing import Any

from anthropic import Anthropic

from src.utils.config import config
from src.utils.logger import get_logger

logger = get_logger(__name__)


class AnthropicClient:
    """Wraps the Anthropic Python SDK with the same interface as BedrockClient."""

    def __init__(self):
        self.client = Anthropic(api_key=config.anthropic_api_key)

    def invoke(
        self,
        system: str,
        messages: list[dict],
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> dict[str, Any]:
        start = time.time()
        response = self.client.messages.create(
            model=config.anthropic_model,
            system=system,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        latency_ms = int((time.time() - start) * 1000)

        return {
            "text": response.content[0].text,
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            },
            "latency_ms": latency_ms,
            "stop_reason": response.stop_reason or "",
        }
