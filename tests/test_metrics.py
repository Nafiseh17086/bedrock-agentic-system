"""Tests for cost and correctness metrics."""

from src.evaluation.metrics import estimate_cost, simple_correctness_check


class TestCostEstimation:
    def test_known_model_uses_correct_rates(self):
        cost = estimate_cost(
            "claude-haiku-4-5-20251001",
            input_tokens=1_000_000,
            output_tokens=1_000_000,
        )
        # Haiku: $1 in + $5 out per 1M tokens = $6 total
        assert cost == 6.0

    def test_unknown_model_uses_fallback_pricing(self):
        cost = estimate_cost(
            "unknown-model-xyz",
            input_tokens=1_000_000,
            output_tokens=1_000_000,
        )
        # Fallback Sonnet-tier: $3 + $15 = $18
        assert cost == 18.0

    def test_zero_tokens_zero_cost(self):
        cost = estimate_cost("claude-haiku-4-5-20251001", 0, 0)
        assert cost == 0.0


class TestCorrectness:
    def test_all_keywords_present_returns_true(self):
        answer = "The Q3 revenue was 127 million, up 18% year over year."
        assert simple_correctness_check(answer, ["127", "18%"]) is True

    def test_missing_keyword_returns_false(self):
        answer = "The Q3 revenue was 127 million."
        assert simple_correctness_check(answer, ["127", "18%"]) is False

    def test_case_insensitive(self):
        answer = "NORTH AMERICA generated the most revenue."
        assert simple_correctness_check(answer, ["north america"]) is True

    def test_empty_keywords_returns_true(self):
        """Edge case: no keywords to check means vacuously true."""
        assert simple_correctness_check("any answer", []) is True
