"""Tests for knowledge base retrieval (local/offline mode)."""

from unittest.mock import patch

from src.tools.knowledge_base import KnowledgeBase


class TestLocalKnowledgeBase:
    @patch("src.tools.knowledge_base.config")
    def test_retrieves_matching_docs(self, mock_config):
        mock_config.execution_mode = "anthropic"
        mock_config.bedrock_knowledge_base_id = ""

        kb = KnowledgeBase()
        # Sample KB has q3_revenue.txt and supply_chain.txt
        results = kb.retrieve("What was Q3 revenue?", top_k=2)

        # Should find at least one document matching "revenue"
        assert len(results) >= 1
        # Top result should be revenue doc (higher keyword overlap)
        assert any("revenue" in r["source"].lower() for r in results)

    @patch("src.tools.knowledge_base.config")
    def test_empty_query_returns_empty(self, mock_config):
        mock_config.execution_mode = "anthropic"
        mock_config.bedrock_knowledge_base_id = ""

        kb = KnowledgeBase()
        results = kb.retrieve("xyzabc_nomatch_qwerty", top_k=3)
        assert results == []

    @patch("src.tools.knowledge_base.config")
    def test_top_k_respected(self, mock_config):
        mock_config.execution_mode = "anthropic"
        mock_config.bedrock_knowledge_base_id = ""

        kb = KnowledgeBase()
        results = kb.retrieve("revenue supply chain risk", top_k=1)
        assert len(results) <= 1
