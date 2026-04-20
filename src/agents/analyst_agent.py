"""Analyst agent — specializes in numerical analysis and comparisons."""

from dataclasses import dataclass

from src.utils.llm_factory import get_llm_client
from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class AnalysisOutput:
    analysis: str
    key_metrics: list[str]


class AnalystAgent:
    """Handles numerical reasoning, trends, and comparisons."""

    SYSTEM = """You are a quantitative analyst. Given a query and optional
research context, produce a numerical analysis. Rules:
- Show your reasoning step-by-step
- Extract specific numbers, trends, and comparisons
- If data is missing, state what would be needed
- End with a bulleted list of key metrics/findings"""

    def __init__(self):
        self.llm = get_llm_client()

    def run(self, query: str, context: str = "") -> AnalysisOutput:
        logger.info(f"📊 [ANALYST] Analyzing: {query[:60]}...")

        user_msg = f"Query: {query}"
        if context:
            user_msg += f"\n\nResearch context to analyze:\n{context}"

        response = self.llm.invoke(
            system=self.SYSTEM,
            messages=[{"role": "user", "content": user_msg}],
        )

        text = response["text"]
        # Extract bullet lines as key metrics
        metrics = [
            line.strip().lstrip("-•*").strip()
            for line in text.split("\n")
            if line.strip().startswith(("-", "•", "*"))
        ]

        return AnalysisOutput(analysis=text, key_metrics=metrics)
