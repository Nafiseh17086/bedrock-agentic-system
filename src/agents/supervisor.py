"""Supervisor agent — routes queries to specialist agents.

Implements a simple planner that decides which agents to invoke
based on the query intent.
"""

import json
from dataclasses import dataclass

from src.utils.llm_factory import get_llm_client
from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class RoutingDecision:
    needs_research: bool
    needs_analysis: bool
    research_query: str = ""
    analysis_query: str = ""
    reasoning: str = ""


class SupervisorAgent:
    """Decides which specialist agents to invoke."""

    SYSTEM = """You are a supervisor agent that routes user queries to specialist agents.

Available specialists:
- RESEARCH_AGENT: Retrieves information from knowledge bases and documents.
- ANALYST_AGENT: Performs numerical analysis, comparisons, and calculations.

For each query, decide which specialists are needed. Respond ONLY with a JSON object:
{
    "needs_research": bool,
    "needs_analysis": bool,
    "research_query": "optimized query for research agent, or empty string",
    "analysis_query": "optimized query for analyst agent, or empty string",
    "reasoning": "brief explanation"
}

Rules:
- If the query asks about facts, documents, or context -> needs_research=true
- If the query involves math, comparison, or trends -> needs_analysis=true
- Both can be true for complex queries.
"""

    def __init__(self):
        self.llm = get_llm_client()

    def route(self, query: str) -> RoutingDecision:
        logger.info(f"🎭 [SUPERVISOR] Routing query: {query[:80]}...")

        response = self.llm.invoke(
            system=self.SYSTEM,
            messages=[{"role": "user", "content": query}],
            temperature=0.0,
        )

        try:
            # Extract JSON from the response (strip markdown fences if present)
            text = response["text"].strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
                text = text.strip()

            data = json.loads(text)
            decision = RoutingDecision(
                needs_research=data.get("needs_research", False),
                needs_analysis=data.get("needs_analysis", False),
                research_query=data.get("research_query", ""),
                analysis_query=data.get("analysis_query", ""),
                reasoning=data.get("reasoning", ""),
            )
            logger.info(
                f"   ↳ Research: {decision.needs_research}, "
                f"Analysis: {decision.needs_analysis}"
            )
            return decision

        except (json.JSONDecodeError, KeyError, IndexError) as e:
            logger.warning(f"Supervisor routing failed, defaulting to both: {e}")
            return RoutingDecision(
                needs_research=True,
                needs_analysis=True,
                research_query=query,
                analysis_query=query,
                reasoning="Fallback: routing failed, using all specialists",
            )
