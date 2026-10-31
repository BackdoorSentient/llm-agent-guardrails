# llm-agent-guardrails

**Guardrails for LLM agents** — schema validation, action allowlisting, and deterministic overrides for LangGraph/LangChain agents. 100% free, runs on Ollama.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

## Why this exists

LLM agents are increasingly trusted to take real actions — calling APIs, writing to databases, triggering workflows — not just answer questions. But LLMs are unreliable decision-makers: they produce malformed output, call tools they shouldn't, and handle edge cases inconsistently. Most agent frameworks (LangChain, LangGraph, AutoGen, CrewAI) focus on making agents *more capable*, not on making them *safer to deploy*.

`llm-agent-guardrails` is a lightweight, reusable layer that sits around any LangGraph node and enforces three things before an agent's output is allowed through:

1. **Schema validation** — every tool call/output is checked against a Pydantic schema before it executes
2. **Action allowlisting** — only pre-approved tools/functions can be called; everything else is blocked and logged
3. **Deterministic overrides** — known-safe input patterns bypass the LLM entirely, for speed and predictability

Every decision is traced via self-hosted Langfuse, and guardrail effectiveness is measured automatically with a DeepEval red-team suite running in CI — so you can prove it works, not just claim it.

Built and tested entirely with **free, local tools** — no paid APIs, no cloud spend required.

## How it works

```
User query
   │
   ▼
LangGraph node (your existing agent logic)
   │
   ▼
GuardedNode wrapper intercepts the output
   ├─ Pydantic schema check  ──────► fail → reprompt once → fallback
   ├─ Allowlist check        ──────► not allowed → blocked + logged
   └─ Deterministic override ──────► pattern match → skip LLM entirely
   │
   ▼
Langfuse logs the decision (proposed / blocked / overridden)
   │
   ▼
Validated output returned
```

A separate **DeepEval red-team suite** runs in GitHub Actions on every push, scoring the guardrail **catch rate** using Ollama as the judge model.

## Tech stack (all free / local)

| Layer | Tool |
|---|---|
| Orchestration | LangGraph + LangChain |
| LLM | Ollama (llama3, qwen2.5:3b-instruct) |
| Schema validation | Pydantic |
| Vector store (optional) | FAISS |
| Observability | Langfuse (self-hosted) |
| Evaluation | DeepEval + Ollama-as-judge |
| CI/CD | GitHub Actions |

## Installation

```bash
git clone https://github.com/BackdoorSentient/llm-agent-guardrails.git
cd llm-agent-guardrails
pip install -e .
```

### Prerequisites

- [Ollama](https://ollama.com) installed and running locally
- Pull the models used by default:
  ```bash
  ollama pull llama3
  ollama pull qwen2.5:3b-instruct
  ```
- (Optional) Docker, for self-hosted Langfuse tracing

## Quick start

```python
from langgraph.graph import StateGraph
from guardrails import GuardedNode
from guardrails.schemas import ToolCallSchema
from guardrails.allowlist import Allowlist

allowlist = Allowlist(["search_docs", "summarize"])

guarded_node = GuardedNode(
    node=your_existing_node,
    schema=ToolCallSchema,
    allowlist=allowlist,
)

graph = StateGraph(...)
graph.add_node("agent_step", guarded_node)
```

See [`examples/`](examples/) for a full working agent.

## Security

This project maps its controls to the **OWASP Top 10 for LLM Applications**:

| Guardrail | Mitigates |
|---|---|
| Schema validation | Insecure Output Handling |
| Action allowlisting | Excessive Agency |
| Deterministic overrides | Reduces Prompt Injection attack surface |

See [`SECURITY.md`](SECURITY.md) for details and how to report a vulnerability.

## Evaluation

Guardrail effectiveness is measured against a red-team dataset of deliberately malformed and off-policy prompts, scored with DeepEval using a local Ollama model as judge.

```bash
pytest tests/eval/ --deepeval
```

Current catch rate and methodology: see [`eval/README.md`](eval/README.md).

## Roadmap

- [x] Schema validation layer
- [x] Action allowlist layer
- [x] Deterministic override layer
- [x] Langfuse tracing integration
- [x] DeepEval red-team suite + GitHub Actions CI
- [ ] Prompt-injection detection module
- [ ] Matrix CI across multiple local models
- [ ] Semantic caching of guardrail decisions
- [ ] Grafana dashboard for catch rate over time

## License

MIT — see [LICENSE](LICENSE).

## Contributing

Issues and PRs welcome. Please read [`SECURITY.md`](SECURITY.md) before reporting any security-related findings.
