"""Cost and performance metrics calculators."""

from dataclasses import dataclass

# Rough $ per 1M tokens — approximate values for reference only
# Real pricing changes; verify at provider docs.
PRICING = {
    # Anthropic direct API (USD per 1M tokens)
    "claude-haiku-4-5-20251001": {"input": 1.0, "output": 5.0},
    "claude-sonnet-4-5": {"input": 3.0, "output": 15.0},
    "claude-opus-4-6": {"input": 15.0, "output": 75.0},
    # Bedrock model IDs
    "anthropic.claude-3-5-sonnet-20241022-v2:0": {"input": 3.0, "output": 15.0},
    "anthropic.claude-3-haiku-20240307-v1:0": {"input": 0.25, "output": 1.25},
}


@dataclass
class RunMetrics:
    approach: str
    latency_ms: int
    input_tokens: int
    output_tokens: int
    estimated_cost_usd: float
    correct: bool | None = None


def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Estimate USD cost given model and token counts."""
    rates = PRICING.get(model)
    if not rates:
        # Unknown model — default to Sonnet-tier pricing
        rates = {"input": 3.0, "output": 15.0}
    return (
        input_tokens * rates["input"] / 1_000_000
        + output_tokens * rates["output"] / 1_000_000
    )


def simple_correctness_check(answer: str, expected_keywords: list[str]) -> bool:
    """Naive accuracy check — are all expected keywords present?

    For production, replace with LLM-as-judge or exact-match per dataset.
    """
    lower_answer = answer.lower()
    return all(kw.lower() in lower_answer for kw in expected_keywords)
