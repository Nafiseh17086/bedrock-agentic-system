"""Input guardrail — filters user queries before they reach agents.

Uses Bedrock Guardrails API when available; falls back to regex-based
PII detection for the local demo.
"""

import re
from dataclasses import dataclass

from src.utils.logger import get_logger

logger = get_logger(__name__)

# Rough PII patterns — production would use Presidio or similar
_EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
_PHONE_RE = re.compile(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b")
_CC_RE = re.compile(r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b")


@dataclass
class GuardrailResult:
    passed: bool
    sanitized_input: str
    flags: list[str]
    reason: str = ""


class InputGuard:
    """Filters and sanitizes user input before agent invocation."""

    BLOCKED_TOPICS = {
        "illegal activities",
        "self-harm instructions",
        "weapon creation",
    }

    def check(self, user_input: str) -> GuardrailResult:
        flags = []
        sanitized = user_input

        # PII redaction
        if _EMAIL_RE.search(sanitized):
            flags.append("email_detected")
            sanitized = _EMAIL_RE.sub("[EMAIL_REDACTED]", sanitized)

        if _SSN_RE.search(sanitized):
            flags.append("ssn_detected")
            sanitized = _SSN_RE.sub("[SSN_REDACTED]", sanitized)

        if _PHONE_RE.search(sanitized):
            flags.append("phone_detected")
            sanitized = _PHONE_RE.sub("[PHONE_REDACTED]", sanitized)

        if _CC_RE.search(sanitized):
            flags.append("credit_card_detected")
            sanitized = _CC_RE.sub("[CARD_REDACTED]", sanitized)

        # Naive topic check — real system would use a classifier
        lower = sanitized.lower()
        for topic in self.BLOCKED_TOPICS:
            if topic in lower:
                logger.warning(f"Blocked topic detected: {topic}")
                return GuardrailResult(
                    passed=False,
                    sanitized_input="",
                    flags=flags + ["blocked_topic"],
                    reason=f"Query blocked: topic '{topic}' is not permitted.",
                )

        if flags:
            logger.info(f"Input sanitized. Flags: {flags}")

        return GuardrailResult(passed=True, sanitized_input=sanitized, flags=flags)
