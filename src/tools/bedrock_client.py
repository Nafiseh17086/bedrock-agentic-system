"""AWS Bedrock client using the Converse API."""

import time
from typing import Any

import boto3
from botocore.exceptions import ClientError

from src.utils.config import config
from src.utils.logger import get_logger

logger = get_logger(__name__)


class BedrockClient:
    """Wraps AWS Bedrock Runtime with the Converse API.

    Converse API is provider-agnostic within Bedrock — you can swap
    Claude for Llama or Mistral without changing this code.
    """

    def __init__(self):
        self.client = boto3.client(
            "bedrock-runtime",
            region_name=config.aws_region,
            aws_access_key_id=config.aws_access_key_id or None,
            aws_secret_access_key=config.aws_secret_access_key or None,
        )

    def invoke(
        self,
        system: str,
        messages: list[dict],
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> dict[str, Any]:
        """Call Bedrock and return normalized output."""
        bedrock_messages = [
            {"role": m["role"], "content": [{"text": m["content"]}]}
            for m in messages
        ]

        kwargs = {
            "modelId": config.bedrock_model_id,
            "messages": bedrock_messages,
            "system": [{"text": system}] if system else [],
            "inferenceConfig": {
                "temperature": temperature,
                "maxTokens": max_tokens,
            },
        }

        # Attach guardrail if configured
        if config.bedrock_guardrail_id:
            kwargs["guardrailConfig"] = {
                "guardrailIdentifier": config.bedrock_guardrail_id,
                "guardrailVersion": config.bedrock_guardrail_version,
            }

        start = time.time()
        try:
            response = self.client.converse(**kwargs)
        except ClientError as e:
            logger.error(f"Bedrock invocation failed: {e}")
            raise
        latency_ms = int((time.time() - start) * 1000)

        text = response["output"]["message"]["content"][0]["text"]
        usage = response.get("usage", {})

        return {
            "text": text,
            "usage": {
                "input_tokens": usage.get("inputTokens", 0),
                "output_tokens": usage.get("outputTokens", 0),
            },
            "latency_ms": latency_ms,
            "stop_reason": response.get("stopReason", ""),
        }
