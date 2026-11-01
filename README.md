# llm-agent-guardrails

**Guardrails for LLM agents** — schema validation, action allowlisting, and deterministic overrides for LangGraph/LangChain agents. 100% free, runs on Ollama.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

> **Status: early / actively being built.** Schema validation and action allowlisting are implemented and tested. Deterministic overrides, the combined `GuardedNode` wrapper, Langfuse tracing, and the DeepEval red-team suite are in progress — see [Roadmap](#roadmap) below for the real current state.

## Why this exists

LLM agents are increasingly trusted to take real actions — calling APIs, writing to databases, triggering workflows — not just answer questions. But LLMs are unreliable decision-makers: they produce malformed output, call tools they shouldn't, and handle edge cases inconsistently. Most agent frameworks (LangChain, LangGraph, AutoGen, CrewAI) focus on making agents *more capable*, not on making them *safer to deploy*.

`llm-agent-guardrails` is a lightweight, reusable layer meant to sit around any LangGraph node and enforce three things before an agent's output is allowed through:

1. **Schema validation** — every tool call/output is checked against a Pydantic schema before it executes
2. **Action allowlisting** — only pre-approved tools/functions can be called; everything else is blocked and logged
3. **Deterministic overrides** — known-safe input patterns bypass the LLM entirely, for speed and predictability (in progress)

Every guardrail decision is logged to a self-hosted PostgreSQL database for inspection, and the plan is to trace decisions via self-hosted Langfuse and measure guardrail effectiveness automatically with a DeepEval red-team suite running in CI.

Built and tested entirely with **free, local tools** — no paid APIs, no cloud spend required.

## How it's meant to work

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
Decision logged (PostgreSQL now; Langfuse tracing planned)
   │
   ▼
Validated output returned
```

A DeepEval red-team suite is planned to run in GitHub Actions on every push, scoring the guardrail **catch rate** using Ollama as the judge model. Right now CI runs the unit test suite (`pytest tests/`).

## Tech stack (all free / local)

| Layer | Tool |
|---|---|
| Orchestration | LangGraph + LangChain |
| LLM | Ollama (llama3.1, qwen2.5:3b-instruct) |
| Schema validation | Pydantic |
| Vector store (demo retrieval) | FAISS |
| Data store | PostgreSQL + pgvector (self-hosted via Docker) |
| Observability | Langfuse (self-hosted, planned) |
| Evaluation | DeepEval + Ollama-as-judge (planned) |
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
  ollama pull llama3.1
  ollama pull qwen2.5:3b-instruct
  ```
- [Docker](https://www.docker.com/), for PostgreSQL and (later) self-hosted Langfuse

### Spin up the local stack

```bash
docker compose up -d
```

Copy `.env.example` to `.env` and adjust if needed, then create the database tables:

```bash
python -m guardrails.services.db_service
```

## Quick start

```python
from guardrails.core.allowlist import Allowlist, ToolNotAllowedError
from guardrails.core.schemas import SearchToolCall

allowlist = Allowlist(["search_docs", "summarize"])

try:
    allowlist.check("search_docs", user_query="example query")
    print("allowed")
except ToolNotAllowedError as exc:
    print(f"blocked: {exc}")
```

See [`examples/basic_demo.py`](examples/basic_demo.py) for a full schema-validation example against a live Ollama model, and [`examples/allowlist_demo.py`](examples/allowlist_demo.py) for the allowlist layer in action. A combined `GuardedNode` wrapper tying all three guardrail layers together is in progress (see [Roadmap](#roadmap)).

## Project structure

```
guardrails/
  core/        # guardrail logic: schemas, allowlist, overrides, GuardedNode wrapper
  services/    # I/O: database connection, LLM calls
  models/      # SQLAlchemy table definitions
  utils/       # logging config, JSON parsing helpers
examples/      # runnable demo scripts
tests/         # unit tests
```

## Security

This project is designed around the **OWASP Top 10 for LLM Applications**:

| Guardrail | Mitigates |
|---|---|
| Schema validation | Insecure Output Handling |
| Action allowlisting | Excessive Agency |
| Deterministic overrides (planned) | Reduces Prompt Injection attack surface |

A `SECURITY.md` with vulnerability-reporting details is planned.

## Roadmap

- [x] Schema validation layer
- [x] Action allowlist layer (with PostgreSQL decision logging)
- [x] Project restructure into `core/` / `services/` / `models/` / `utils/`
- [x] Basic CI (pytest on push/PR)
- [ ] Deterministic override layer
- [ ] Combined `GuardedNode` wrapper
- [ ] Langfuse tracing integration
- [ ] Red-team dataset + DeepEval scoring
- [ ] CI extended to run the eval suite and fail on catch-rate regression
- [ ] `SECURITY.md`
- [ ] Matrix CI across multiple local models
- [ ] Demo UI (Chainlit)
- [ ] Semantic caching of guardrail decisions
- [ ] Grafana dashboard for catch rate over time

## License

MIT — see [LICENSE](LICENSE).

## Contributing

Issues and PRs welcome.