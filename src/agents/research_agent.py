"""Research agent — specializes in retrieving and summarizing information."""

from dataclasses import dataclass

from src.tools.knowledge_base import KnowledgeBase
from src.utils.llm_factory import get_llm_client
from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ResearchOutput:
    findings: str
    sources: list[str]
    retrieved_chunks: int


class ResearchAgent:
    """Handles fact-finding via knowledge base retrieval."""

    SYSTEM = """You are a research specialist. Given a query and retrieved context,
produce a concise factual summary. Rules:
- Only use information from the provided context
- If context is insufficient, explicitly say so
- Cite sources using [source_name] inline
- Be concise (3-5 sentences unless more detail is needed)"""

    def __init__(self):
        self.llm = get_llm_client()
        self.kb = KnowledgeBase()

    def run(self, query: str, top_k: int = 3) -> ResearchOutput:
        logger.info(f"🔍 [RESEARCH] Retrieving for: {query[:60]}...")

        chunks = self.kb.retrieve(query, top_k=top_k)

        if not chunks:
            return ResearchOutput(
                findings="No relevant information found in the knowledge base.",
                sources=[],
                retrieved_chunks=0,
            )

        context = "\n\n".join(
            f"[{c['source']}]\n{c['content']}" for c in chunks
        )

        response = self.llm.invoke(
            system=self.SYSTEM,
            messages=[
                {
                    "role": "user",
                    "content": f"Query: {query}\n\nContext:\n{context}",
                }
            ],
        )

        return ResearchOutput(
            findings=response["text"],
            sources=[c["source"] for c in chunks],
            retrieved_chunks=len(chunks),
        )
