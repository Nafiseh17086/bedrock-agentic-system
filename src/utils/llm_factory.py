"""Unified LLM client — abstracts Bedrock vs direct Anthropic."""

from __future__ import annotations

from src.utils.config import config
from src.utils.logger import get_logger

logger = get_logger(__name__)


class LLMClient:
    """A single interface for invoking LLMs regardless of backend.

    Under the hood it dispatches to either Bedrock (boto3) or the
    Anthropic Python SDK depending on EXECUTION_MODE.
    """

    def __init__(self):
        self.mode = config.execution_mode
        if self.mode == "bedrock":
            from src.tools.bedrock_client import BedrockClient

            self._client = BedrockClient()
            self.model_id = config.bedrock_model_id
        else:
            from src.tools.anthropic_client import AnthropicClient

            self._client = AnthropicClient()
            self.model_id = config.anthropic_model

    def invoke(
        self,
        system: str,
        messages: list[dict],
        temperature: float | None = None,
        max_tokens: int = 4096,
    ) -> dict:
        """Invoke the LLM with a system prompt and a list of messages.

        Args:
            system: System prompt string.
            messages: List of {"role": "user"|"assistant", "content": str}.
            temperature: Override default temperature.
            max_tokens: Max response tokens.

        Returns:
            Dict with keys: "text", "usage" (input_tokens, output_tokens), "latency_ms".
        """
        temp = temperature if temperature is not None else config.llm_temperature
        return self._client.invoke(
            system=system,
            messages=messages,
            temperature=temp,
            max_tokens=max_tokens,
        )


def get_llm_client() -> LLMClient:
    return LLMClient()
