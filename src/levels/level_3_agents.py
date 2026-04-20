"""Level 3: Full multi-agent orchestration.

Supervisor routes the query to specialists (research, analyst), then a
synthesizer merges outputs. Guardrails wrap input and output.
"""

import time

from src.agents.analyst_agent import AnalystAgent
from src.agents.research_agent import ResearchAgent
from src.agents.supervisor import SupervisorAgent
from src.agents.synthesizer import SynthesizerAgent
from src.guardrails.input_guard import InputGuard
from src.guardrails.output_guard import OutputGuard
from src.utils.logger import get_logger

logger = get_logger(__name__)


def run_level_3(query: str) -> dict:
    logger.info("🟥 [LEVEL 3] Multi-agent orchestration")
    start = time.time()

    # --- Input guardrail ---
    input_guard = InputGuard()
    guard_result = input_guard.check(query)

    if not guard_result.passed:
        return {
            "level": 3,
            "approach": "agents",
            "answer": guard_result.reason,
            "blocked": True,
            "flags": guard_result.flags,
            "latency_ms": int((time.time() - start) * 1000),
        }

    sanitized = guard_result.sanitized_input

    # --- Supervisor routing ---
    supervisor = SupervisorAgent()
    routing = supervisor.route(sanitized)

    # --- Specialist agents ---
    research_text = ""
    sources: list[str] = []
    analysis_text = ""

    if routing.needs_research:
        researcher = ResearchAgent()
        r_out = researcher.run(routing.research_query or sanitized)
        research_text = r_out.findings
        sources = r_out.sources

    if routing.needs_analysis:
        analyst = AnalystAgent()
        a_out = analyst.run(
            routing.analysis_query or sanitized,
            context=research_text,
        )
        analysis_text = a_out.analysis

    # --- Synthesize ---
    synthesizer = SynthesizerAgent()
    final_answer = synthesizer.run(
        original_query=sanitized,
        research_output=research_text,
        analysis_output=analysis_text,
    )

    # --- Output guardrail ---
    output_guard = OutputGuard()
    output_result = output_guard.check(final_answer)

    total_ms = int((time.time() - start) * 1000)

    return {
        "level": 3,
        "approach": "agents",
        "answer": output_result.cleaned_output,
        "blocked": False,
        "input_flags": guard_result.flags,
        "output_flags": output_result.flags,
        "routing": {
            "research": routing.needs_research,
            "analysis": routing.needs_analysis,
            "reasoning": routing.reasoning,
        },
        "sources": sources,
        "latency_ms": total_ms,
    }
