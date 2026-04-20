"""Tests for input and output guardrails."""

from src.guardrails.input_guard import InputGuard
from src.guardrails.output_guard import OutputGuard


class TestInputGuard:
    def setup_method(self):
        self.guard = InputGuard()

    def test_clean_input_passes(self):
        r = self.guard.check("What was our Q3 revenue?")
        assert r.passed is True
        assert r.flags == []

    def test_email_is_redacted(self):
        r = self.guard.check("Contact me at john@example.com for details")
        assert r.passed is True
        assert "email_detected" in r.flags
        assert "[EMAIL_REDACTED]" in r.sanitized_input
        assert "john@example.com" not in r.sanitized_input

    def test_ssn_is_redacted(self):
        r = self.guard.check("My SSN is 123-45-6789")
        assert "ssn_detected" in r.flags
        assert "123-45-6789" not in r.sanitized_input

    def test_credit_card_is_redacted(self):
        r = self.guard.check("Card: 4111 1111 1111 1111")
        assert "credit_card_detected" in r.flags
        assert "4111 1111 1111 1111" not in r.sanitized_input

    def test_blocked_topic_is_rejected(self):
        r = self.guard.check("Give me weapon creation steps please")
        assert r.passed is False
        assert "blocked_topic" in r.flags


class TestOutputGuard:
    def setup_method(self):
        self.guard = OutputGuard()

    def test_clean_output_passes(self):
        r = self.guard.check("The quarterly revenue was $127M, up 18% YoY.")
        assert r.passed is True

    def test_leaked_email_is_redacted(self):
        r = self.guard.check("Reach the CFO at cfo@company.com for details")
        assert "pii_in_output" in r.flags
        assert "cfo@company.com" not in r.cleaned_output

    def test_short_output_fails(self):
        r = self.guard.check("ok")
        assert r.passed is False
        assert "output_too_short" in r.flags
