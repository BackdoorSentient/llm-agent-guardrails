# Project memory

Durable facts for this repo. Update only via the `update-memory` skill (or when the user explicitly asks to remember / forget / update memory).

Last updated: 2026-11-01

## Preferences

- Deep analysis: when the user says analyze, do a thorough evidence-based investigation (personal skill `analyze`).
- Explanation style: `detailed-explain-mode` and `one-line-explain-mode` exist as personal skills; follow the one the user attaches or names.

## User / environment

- Cursor plan: free. Included usage refills monthly; paid-only modes (including Low) are unavailable unless upgraded.

## Project

- Workspace: `d:\projects\llm-agent-guardrails`
- Public repo: `https://github.com/BackdoorSentient/llm-agent-guardrails` (MIT, import name `guardrails`)
- Product: a pip-installable safety layer for LangGraph/LangChain agents — Pydantic schema validation, action allowlisting, deterministic overrides — not a RAG app and not a multi-agent orchestrator
- Origin: generalizes the MatchOS node-boundary guardrail pattern into a reusable open-source package
- Constraint: free/local tools only (Ollama, no paid APIs, no cloud spend)
- Default models: `llama3` (main agent) and `qwen2.5:3b-instruct` (weaker model to stress-test rails)
- Intended stack: LangGraph + LangChain, Pydantic, self-hosted Langfuse, DeepEval, GitHub Actions; FAISS only if a demo needs retrieval
- Status: docs and README exist; the Python package, examples, eval suite, and CI are not implemented yet (README roadmap checkboxes are aspirational)

## Decisions

- v1 core is the library plus tracing and eval: `guardrails/schemas.py`, `allowlist.py`, `overrides.py`, Langfuse, red-team catch-rate, `pyproject.toml`
- Postgres, Chainlit, Grafana, FastAPI wrapper, and MkDocs are demo or later — not required to install the package
- Allowlist v1 is a config-driven permitted-tool list, not a database
- Cube.js is out of scope

## Do not forget

- GuardedNode hook order is still unresolved: overrides must run before the LLM if they skip the model; schema and allowlist must run before tool execution
- Do not treat `Project Memory — LLM Guardrails & Learning Roadmap.md` as a public spec; keep durable facts here instead of committing that file
- Catch-rate CI cannot assume GitHub-hosted runners have Ollama; prefer labeled pytest for the merge gate
