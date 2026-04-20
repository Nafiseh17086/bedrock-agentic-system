"""Level 1: Naive prompt call.

Baseline for comparison. Just sends the query to the LLM with no
retrieval, no tools, no orchestration.
"""

from src.utils.llm_factory import get_llm_client
from src.utils.logger import get_logger

logger = get_logger(__name__)


def run_level_1(query: str) -> dict:
    """Execute a plain prompt call and return response + metadata."""
    logger.info("🟦 [LEVEL 1] Plain prompt call")

    llm = get_llm_client()
    response = llm.invoke(
        system="You are a helpful assistant. Answer concisely and factually.",
        messages=[{"role": "user", "content": query}],
    )

    return {
        "level": 1,
        "approach": "prompt_only",
        "answer": response["text"],
        "latency_ms": response["latency_ms"],
        "input_tokens": response["usage"]["input_tokens"],
        "output_tokens": response["usage"]["output_tokens"],
    }
