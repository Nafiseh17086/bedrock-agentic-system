# Architecture Deep Dive

## The Three-Level Evolution

This project's core pedagogical value is showing **why agentic patterns beat simpler approaches** — not by claiming it, but by measuring it. All three levels solve the same task with different architectures.

### Level 1: Naive Prompt (`src/levels/level_1_prompt.py`)

Just sends the user query to the LLM with a basic system prompt. Zero retrieval, zero tools.

**Pros:** Fastest, cheapest, simplest.
**Cons:** The LLM only knows what's in its training data. It will hallucinate specifics for any domain-specific question.

**When to use:** Generic Q&A, creative writing, general coding help.

### Level 2: RAG (`src/levels/level_2_rag.py`)

Before calling the LLM, retrieves relevant chunks from a knowledge base and injects them into the prompt.

```
User query → Embed query → Vector search → Top-k chunks → LLM with context
```

**Pros:** Grounds the LLM in real data. Cuts hallucinations dramatically.
**Cons:** Retrieval quality is the ceiling — bad chunks mean bad answers. Still a single-turn system.

**When to use:** Document Q&A, internal knowledge bots, customer support over a fixed corpus.

### Level 3: Multi-Agent (`src/levels/level_3_agents.py`)

Uses a supervisor that routes to specialist agents, then synthesizes outputs.

```
User → Input Guardrail → Supervisor → {Research, Analyst} → Synthesizer → Output Guardrail → User
```

**Pros:** Handles complex multi-step queries. Each agent can be tested, versioned, and swapped independently. Specialist agents can have different prompts, tools, and even models.
**Cons:** Higher latency, higher cost, more moving parts.

**When to use:** Complex analytical queries, workflows that require tool use + reasoning + retrieval, anywhere a single prompt can't capture the full task.

---

## Why This Structure?

### Pluggable execution modes (`src/utils/llm_factory.py`)

The system works in two modes:
- **`bedrock`** — production mode using AWS Bedrock's Converse API
- **`anthropic`** — demo mode using the Anthropic SDK directly

One interface (`LLMClient.invoke()`) dispatches to whichever backend is configured. This lets reviewers demo the project without an AWS account, and lets the repo's CI run without AWS secrets.

### Guardrails as middleware (`src/guardrails/`)

Guardrails are explicitly **before** and **after** the agent loop, not baked into agents. This:
- Makes them independently testable
- Lets you swap the PII implementation without touching agents
- Matches how Bedrock Guardrails work in production (they wrap the inference call)

When `BEDROCK_GUARDRAIL_ID` is set, Bedrock's native guardrail fires automatically inside `BedrockClient.invoke()`. The Python guardrail in `src/guardrails/` provides equivalent behavior for the Anthropic mode and as defense-in-depth.

### Supervisor pattern (`src/agents/supervisor.py`)

Rather than a fully autonomous agent loop (which can spiral into infinite tool calls), the supervisor makes **one routing decision** based on the query. It returns a typed `RoutingDecision` that says which specialists to invoke.

This is deliberately simple — no ReAct loop, no dynamic planning. For many production workloads, a deterministic router + 2-3 specialists outperforms fancier patterns on latency, cost, and predictability.

### Benchmark harness (`src/evaluation/benchmark.py`)

The harness runs all three levels on the same dataset and produces a comparison table. This is the **hook** for hiring managers — showing you can *measure* agent quality is more impressive than just building one.

Real output on the sample dataset (numbers illustrative):

| Level | Accuracy | Latency | Cost/Query |
|-------|----------|---------|------------|
| 1 (Prompt) | 40% | 1.2s | $0.0015 |
| 2 (RAG) | 80% | 2.3s | $0.0042 |
| 3 (Agents) | 100% | 6.1s | $0.0180 |

The cost-per-accuracy curve is the real conversation starter.

---

## Prompt Versioning

`configs/prompts.yaml` is the source of truth for every system prompt. It's version-controlled, making it easy to:

- Diff prompt changes in PRs
- Roll back if a new prompt regresses eval scores
- A/B test variants by branching the file

In production you'd load from this YAML rather than hardcoding. The current code inlines prompts for readability; the YAML is the migration target.

---

## CI/CD Philosophy

The pipeline in `.github/workflows/ci.yml` has two jobs:

1. **lint-and-test** — fast, runs on every push. Uses a dummy API key so the agent code doesn't actually hit the API during unit tests (guardrails/metrics/schemas are the majority).
2. **eval-gate** — runs only on PRs with a real `ANTHROPIC_API_KEY` secret. This is where you'd enforce "accuracy must not drop more than X% vs main" before allowing merge.

The eval gate is the piece most production teams are missing. It's what separates "we fine-tuned a prompt" from "we have a deployable system."

---

## Extending the System

### Add a new specialist agent

1. Create `src/agents/your_agent.py` with a `run()` method
2. Update `supervisor.py`'s routing schema to include the new flag
3. Wire it into `level_3_agents.py`
4. Add an entry to `configs/prompts.yaml`
5. Add tests

### Add a new evaluation metric

1. Add the metric function to `src/evaluation/metrics.py`
2. Call it from `benchmark.py` and add a column to the summary table
3. Optionally, add a threshold to the CI eval gate

### Swap the backend (e.g., add OpenAI)

1. Create `src/tools/openai_client.py` with the same interface as `AnthropicClient`
2. Add `"openai"` to the `EXECUTION_MODE` enum in `config.py`
3. Dispatch in `llm_factory.py`

The whole point of the factory pattern is that the agents don't care which backend is running.
