"""Level 2: Retrieval-Augmented Generation.

Adds a knowledge base lookup before the LLM call. Dramatically improves
accuracy on domain-specific questions, at modest latency/cost overhead.
"""

import time

from src.tools.knowledge_base import KnowledgeBase
from src.utils.llm_factory import get_llm_client
from src.utils.logger import get_logger

logger = get_logger(__name__)

RAG_SYSTEM = """You are a helpful assistant. Answer the user's question using ONLY the provided
context. If the context doesn't contain the answer, say so explicitly.
Cite sources inline using [source_name]."""


def run_level_2(query: str, top_k: int = 3) -> dict:
    logger.info("🟩 [LEVEL 2] RAG with knowledge base")
    start = time.time()

    kb = KnowledgeBase()
    chunks = kb.retrieve(query, top_k=top_k)

    if chunks:
        context = "\n\n".join(
            f"[{c['source']}]\n{c['content']}" for c in chunks
        )
        user_msg = f"Question: {query}\n\nContext:\n{context}"
    else:
        user_msg = (
            f"Question: {query}\n\nContext: (no relevant documents found)"
        )

    llm = get_llm_client()
    response = llm.invoke(
        system=RAG_SYSTEM,
        messages=[{"role": "user", "content": user_msg}],
    )

    total_ms = int((time.time() - start) * 1000)

    return {
        "level": 2,
        "approach": "rag",
        "answer": response["text"],
        "latency_ms": total_ms,
        "input_tokens": response["usage"]["input_tokens"],
        "output_tokens": response["usage"]["output_tokens"],
        "retrieved_chunks": len(chunks),
        "sources": [c["source"] for c in chunks],
    }
