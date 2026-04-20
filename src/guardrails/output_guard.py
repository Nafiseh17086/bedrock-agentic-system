"""Output guardrail — validates agent responses before returning to user."""

import re
from dataclasses import dataclass

from src.utils.logger import get_logger

logger = get_logger(__name__)

_PII_PATTERNS = [
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"), "[EMAIL_REDACTED]"),
    (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "[SSN_REDACTED]"),
    (re.compile(r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b"), "[CARD_REDACTED]"),
]


@dataclass
class OutputCheckResult:
    passed: bool
    cleaned_output: str
    flags: list[str]


class OutputGuard:
    """Sanitizes agent output — catches hallucinated PII, ensures basic quality."""

    MIN_LENGTH = 10

    def check(self, output: str) -> OutputCheckResult:
        flags = []
        cleaned = output

        # Redact any PII that might have leaked through
        for pattern, replacement in _PII_PATTERNS:
            if pattern.search(cleaned):
                flags.append("pii_in_output")
                cleaned = pattern.sub(replacement, cleaned)

        # Quality floor
        if len(cleaned.strip()) < self.MIN_LENGTH:
            flags.append("output_too_short")
            logger.warning("Output below minimum length threshold")
            return OutputCheckResult(
                passed=False,
                cleaned_output=cleaned,
                flags=flags,
            )

        return OutputCheckResult(passed=True, cleaned_output=cleaned, flags=flags)
