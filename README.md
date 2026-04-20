# 🛡️ Bedrock Agentic AI System

> A production-grade **multi-agent system** built on **AWS Bedrock** that demonstrates the shift from single prompt calls → RAG → orchestrated agents. Includes **Bedrock Guardrails**, **CI/CD pipelines**, and **benchmarking harness** for measuring agent precision, latency, and cost.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![AWS Bedrock](https://img.shields.io/badge/AWS-Bedrock-FF9900.svg)](https://aws.amazon.com/bedrock/)
[![Anthropic](https://img.shields.io/badge/Anthropic-Claude-D97757.svg)](https://anthropic.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://img.shields.io/badge/CI-GitHub_Actions-2088FF.svg)](.github/workflows/ci.yml)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

## 🎯 What This Project Demonstrates

This project traces **the entire evolution** of how you build with LLMs in production:

1. **Level 1 — Simple prompt calls** (baseline)
2. **Level 2 — RAG** (retrieval-augmented generation)
3. **Level 3 — Multi-agent orchestration** (specialized agents collaborating)

Plus the production concerns real teams face:
- 🛡️ **Bedrock Guardrails** for content filtering & PII redaction
- 📊 **Benchmarking harness** tracking latency, cost, and accuracy
- 🔁 **CI/CD** with prompt versioning, eval gates, and repeatable deploys
- 🔍 **Observability** via CloudWatch + structured logging

Built for engineers who want to show they understand LLMs as **systems engineering**, not just prompt writing.

---

## 🏗️ Architecture

```
                    ┌─────────────────┐
                    │   User Query    │
                    └────────┬────────┘
                             │
                             ▼
                 ┌───────────────────────┐
                 │  Bedrock Guardrail    │  ◄─── Input filtering
                 │  (Input)              │        (PII, toxicity)
                 └───────────┬───────────┘
                             │
                             ▼
                 ┌───────────────────────┐
                 │   SUPERVISOR AGENT    │  ◄─── Routes to specialists
                 │   (Orchestrator)      │
                 └───┬───────────┬───────┘
                     │           │
         ┌───────────┘           └──────────┐
         ▼                                  ▼
┌─────────────────┐              ┌─────────────────┐
│  RESEARCH       │              │  ANALYST        │
│  AGENT          │              │  AGENT          │
│  (RAG + Web)    │              │  (Calculation)  │
└────────┬────────┘              └────────┬────────┘
         │                                │
         └────────────┬───────────────────┘
                      ▼
           ┌───────────────────────┐
           │  SYNTHESIZER AGENT    │  ◄─── Combines outputs
           └───────────┬───────────┘
                       │
                       ▼
           ┌───────────────────────┐
           │  Bedrock Guardrail    │  ◄─── Output filtering
           │  (Output)             │
           └───────────┬───────────┘
                       │
                       ▼
           ┌───────────────────────┐
           │   Final Response      │
           │   + Audit Trail       │
           └───────────────────────┘
```

See [`docs/architecture.md`](docs/architecture.md) for details on each layer.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🎭 **3 Evolution Levels** | Same task implemented as prompt → RAG → agents, with benchmarks |
| 🛡️ **Bedrock Guardrails** | Content filtering, PII redaction, topic denial |
| 📚 **Knowledge Base RAG** | Vector search over your documents via Bedrock KB |
| ⚡ **Multi-Agent Orchestration** | Supervisor pattern with specialist agents |
| 📊 **Eval Harness** | Precision, latency, cost tracking per pipeline |
| 🔁 **Prompt Versioning** | All prompts stored in YAML, version-controlled |
| 🚀 **CI/CD Ready** | GitHub Actions pipeline with eval gates |
| 🔧 **Dual Mode** | Runs on Bedrock OR direct Anthropic API (no AWS needed to demo) |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- **Either:**
  - AWS account with Bedrock access (production mode), OR
  - An Anthropic API key (demo mode — works without AWS)

### Installation

```bash
git clone https://github.com/Nafiseh17086/bedrock-agentic-system.git
cd bedrock-agentic-system

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env with your credentials
```

### Run the Evolution Demo

See all three levels side-by-side:

```bash
# Level 1: Naive prompt call
python -m src.main --level 1 --query "Summarize the key risks in our Q3 report"

# Level 2: RAG with knowledge base
python -m src.main --level 2 --query "What did we say about supply chain last quarter?"

# Level 3: Full multi-agent system
python -m src.main --level 3 --query "Compare our revenue to top 3 competitors and flag risks"
```

### Run Benchmarks

```bash
python -m src.evaluation.benchmark --dataset examples/eval_dataset.jsonl
```

Output:
```
Level 1 (Prompt)  | Accuracy: 62% | Latency: 1.2s | Cost: $0.003/query
Level 2 (RAG)     | Accuracy: 81% | Latency: 2.1s | Cost: $0.008/query
Level 3 (Agents)  | Accuracy: 94% | Latency: 5.8s | Cost: $0.024/query
```

---

## 🔧 Configuration

Edit `.env`:

```env
# Execution mode: "bedrock" (uses AWS) or "anthropic" (direct API, no AWS needed)
EXECUTION_MODE=anthropic

# AWS (only needed if EXECUTION_MODE=bedrock)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
BEDROCK_MODEL_ID=anthropic.claude-sonnet-4-20250514-v1:0
BEDROCK_GUARDRAIL_ID=
BEDROCK_KNOWLEDGE_BASE_ID=

# Anthropic direct (only needed if EXECUTION_MODE=anthropic)
ANTHROPIC_API_KEY=

# Optional: enable detailed metrics
ENABLE_METRICS=true
```

---

## 📁 Project Structure

```
bedrock-agentic-system/
├── src/
│   ├── agents/
│   │   ├── supervisor.py          # Orchestrator agent
│   │   ├── research_agent.py      # Handles RAG + web lookup
│   │   ├── analyst_agent.py       # Numerical analysis
│   │   └── synthesizer.py         # Combines outputs
│   ├── tools/
│   │   ├── bedrock_client.py      # AWS Bedrock wrapper
│   │   ├── anthropic_client.py    # Fallback direct API client
│   │   └── knowledge_base.py      # RAG retrieval
│   ├── guardrails/
│   │   ├── input_guard.py         # PII + toxicity filtering
│   │   └── output_guard.py        # Response validation
│   ├── evaluation/
│   │   ├── benchmark.py           # Eval harness
│   │   └── metrics.py             # Precision/latency/cost
│   ├── utils/
│   │   ├── config.py              # Env & settings
│   │   ├── llm_factory.py         # Bedrock ↔ Anthropic swap
│   │   └── logger.py
│   ├── levels/                    # Evolution demo
│   │   ├── level_1_prompt.py
│   │   ├── level_2_rag.py
│   │   └── level_3_agents.py
│   └── main.py                    # CLI entry
├── configs/
│   ├── prompts.yaml               # Version-controlled prompts
│   └── guardrail_policy.json      # Bedrock guardrail config
├── examples/
│   ├── eval_dataset.jsonl
│   └── sample_knowledge_base/
├── tests/
├── scripts/
│   └── setup_bedrock_resources.sh
├── .github/workflows/ci.yml
├── requirements.txt
├── LICENSE
└── README.md
```

---

## 🧪 Testing

```bash
pytest                              # All tests
pytest --cov=src --cov-report=html  # With coverage
pytest -m "not aws"                 # Skip AWS-requiring tests
```

---

## 🚢 CI/CD Pipeline

The GitHub Actions workflow in `.github/workflows/ci.yml`:
1. Runs linting (ruff + black)
2. Runs unit tests with coverage
3. Runs eval suite on sample dataset
4. **Blocks merge** if accuracy drops >5% vs baseline
5. Tags successful commits as deployable

---

## 🛠️ Tech Stack

- **[AWS Bedrock](https://aws.amazon.com/bedrock/)** — Managed LLM hosting
- **[Bedrock Guardrails](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html)** — Content safety
- **[Bedrock Knowledge Bases](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html)** — Managed RAG
- **[boto3](https://boto3.amazonaws.com/)** — AWS SDK
- **[Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python)** — Direct API fallback
- **[Pydantic](https://docs.pydantic.dev/)** — Data validation
- **[Rich](https://github.com/Textualize/rich)** — CLI formatting

---

## 🗺️ Roadmap

- [ ] Terraform module for one-command AWS setup
- [ ] Streaming responses via Bedrock Converse API
- [ ] Multi-turn conversation memory (DynamoDB)
- [ ] A/B testing framework for prompt variants
- [ ] Cost alerting via CloudWatch

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## 📄 License

MIT — see [LICENSE](LICENSE).

---

## 👤 Author

**Nafiseh Mollaei**
- GitHub: [@Nafiseh17086](https://github.com/Nafiseh17086)
- LinkedIn: [linkedin.com/in/Nafiseh17086](https://linkedin.com/in/Nafiseh17086)

---

⭐ **If this helped you understand agentic systems, give it a star!**
