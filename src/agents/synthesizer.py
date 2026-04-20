"""Synthesizer agent — merges outputs from specialists into a final response."""

from src.utils.llm_factory import get_llm_client
from src.utils.logger import get_logger

logger = get_logger(__name__)


class SynthesizerAgent:
    """Combines research + analysis into a coherent final answer."""

    SYSTEM = """You are a synthesizer agent. Combine the outputs from specialist
agents into a single, coherent response to the user's original question. Rules:
- Lead with the direct answer to the user's question
- Integrate research findings and analysis (don't just paste them)
- Preserve citations from the research agent
- Be structured but not overly formal — use headers only if needed
- Flag any contradictions between specialists explicitly"""

    def __init__(self):
        self.llm = get_llm_client()

    def run(
        self,
        original_query: str,
        research_output: str = "",
        analysis_output: str = "",
    ) -> str:
        logger.info("🧩 [SYNTHESIZER] Merging specialist outputs")

        sections = [f"Original question: {original_query}"]
        if research_output:
            sections.append(f"Research findings:\n{research_output}")
        if analysis_output:
            sections.append(f"Analysis:\n{analysis_output}")

        user_content = "\n\n---\n\n".join(sections)

        response = self.llm.invoke(
            system=self.SYSTEM,
            messages=[{"role": "user", "content": user_content}],
        )
        return response["text"]
