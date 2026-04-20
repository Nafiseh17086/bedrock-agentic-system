# Contributing

Thanks for your interest! PRs, issues, and ideas are all welcome.

## Development Setup

```bash
git clone https://github.com/YOUR_USERNAME/bedrock-agentic-system.git
cd bedrock-agentic-system
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

For the easiest onboarding, set `EXECUTION_MODE=anthropic` in `.env` — you only need an Anthropic API key, no AWS setup.

## Running Tests

```bash
pytest                              # All tests
pytest --cov=src --cov-report=html  # With coverage report
pytest -m "not aws"                 # Skip AWS-requiring tests
pytest tests/test_guardrails.py     # Single file
```

## Code Style

```bash
black src/ tests/          # Format
ruff check src/ tests/     # Lint
mypy src/                  # Type check (best-effort)
```

Run all three before submitting a PR.

## Pull Request Checklist

- [ ] Tests added for new behavior
- [ ] All tests pass locally
- [ ] `black` and `ruff` are clean
- [ ] Docs updated if behavior changed
- [ ] If prompts changed, bumped the version in `configs/prompts.yaml`
- [ ] If the change could affect eval metrics, ran `python -m src.evaluation.benchmark` and noted the result in the PR

## Good First Issues

- 🔌 Add an OpenAI client as a third `EXECUTION_MODE`
- 🧪 Add LLM-as-judge to `evaluation/metrics.py` (replace keyword match)
- 📊 Streamlit dashboard for benchmark results
- 🌍 Multi-language support in prompts
- 🏗️ Terraform module for automated AWS setup

## Questions

Open an issue — happy to discuss architecture, design tradeoffs, or anything else.
