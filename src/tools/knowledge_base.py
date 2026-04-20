"""Bedrock Knowledge Base retrieval for RAG.

Falls back to a simple in-memory keyword matcher when AWS is unavailable,
so Level 2 (RAG) can still be demo'd without AWS setup.
"""

from pathlib import Path
from typing import Any

import boto3
from botocore.exceptions import ClientError

from src.utils.config import config
from src.utils.logger import get_logger

logger = get_logger(__name__)

_SAMPLE_DOCS_PATH = Path(__file__).parent.parent.parent / "examples" / "sample_knowledge_base"


class KnowledgeBase:
    """Retrieves relevant chunks for a query.

    In Bedrock mode: uses Bedrock Knowledge Base (managed vector store).
    In Anthropic mode: uses a naive keyword scorer over local text files.
    """

    def __init__(self):
        self.use_bedrock = (
            config.execution_mode == "bedrock"
            and bool(config.bedrock_knowledge_base_id)
        )
        if self.use_bedrock:
            self.client = boto3.client(
                "bedrock-agent-runtime", region_name=config.aws_region
            )
        else:
            self._local_docs = self._load_local_docs()

    def _load_local_docs(self) -> list[dict]:
        """Load local sample docs for offline RAG demo."""
        docs = []
        if _SAMPLE_DOCS_PATH.exists():
            for f in _SAMPLE_DOCS_PATH.glob("*.txt"):
                docs.append({"title": f.stem, "content": f.read_text()})
        return docs

    def retrieve(self, query: str, top_k: int = 3) -> list[dict[str, Any]]:
        """Retrieve top-k relevant chunks for the query."""
        if self.use_bedrock:
            return self._retrieve_bedrock(query, top_k)
        return self._retrieve_local(query, top_k)

    def _retrieve_bedrock(self, query: str, top_k: int) -> list[dict[str, Any]]:
        try:
            response = self.client.retrieve(
                knowledgeBaseId=config.bedrock_knowledge_base_id,
                retrievalQuery={"text": query},
                retrievalConfiguration={
                    "vectorSearchConfiguration": {"numberOfResults": top_k}
                },
            )
            return [
                {
                    "content": r["content"]["text"],
                    "source": r.get("location", {}).get("s3Location", {}).get("uri", ""),
                    "score": r.get("score", 0.0),
                }
                for r in response.get("retrievalResults", [])
            ]
        except ClientError as e:
            logger.error(f"KB retrieval failed: {e}")
            return []

    def _retrieve_local(self, query: str, top_k: int) -> list[dict[str, Any]]:
        """Naive keyword-overlap retrieval for the offline demo."""
        q_tokens = set(query.lower().split())
        scored = []
        for doc in self._local_docs:
            d_tokens = set(doc["content"].lower().split())
            overlap = len(q_tokens & d_tokens)
            if overlap > 0:
                scored.append(
                    {
                        "content": doc["content"][:1500],
                        "source": doc["title"],
                        "score": overlap / max(len(q_tokens), 1),
                    }
                )
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]
