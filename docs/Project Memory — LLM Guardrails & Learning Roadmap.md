# Project Memory — LLM Agent Guardrails Framework

Oct 31, 2026 · @Aniket

Context file for new chats — paste this doc's link at the start of a new conversation so Claude can pick up where this left off.

## Background

- 4.2+ years experience, Backend & GenAI Engineer. Birlasoft (Aug 2022-Jan 2026), now R Systems as AI Engineer (Feb 2026-present).
- Stack: Python, FastAPI, LangChain, LangGraph, PostgreSQL/pgvector, Docker.
- Key recent work: MatchOS (R Systems) - a guardrailed, manifest-driven LangGraph pipeline using Claude in a narrow role, RAG on pgvector + Vertex AI embeddings, runtime guardrails (allowlisting, schema validation, deterministic overrides), Langfuse tracing, deployed on Cloud Run + AWS Lambda/S3.
- GitHub: github.com/BackdoorSentient - repos reviewed: genai-raga-langgraph (flagship, pinned), genai\_rag\_service (overlaps with flagship, candidate to archive/merge), Agent\_Eval\_Lab (DeepEval + Langfuse + Ollama agent eval lab, mostly theoretical Q&A content currently).
- Found and resolved: .env files were tracked in all three repos; confirmed harmless placeholder content, not real secrets. Still worth git rm --cached .env plus .gitignore plus .env.example for convention.
- Hard constraint: free/local tools only - no paid APIs, no cloud spend.

## Decision: next project

**LLM Guardrails** (repo/package name: agent-guardrails or similar) - a reusable, pip-installable Python package adding safety guardrails to any LangGraph/LangChain agent: schema validation, action allowlisting, deterministic overrides.

Chosen over a pgvector RAG starter kit, an Agent\_Eval\_Lab regression-suite extension, and a multi-agent-orchestration learning track, because it directly generalizes the real guardrail work done at MatchOS, is rare on GitHub (most portfolios are RAG-app clones), and turns the free/local constraint into a feature - local models fail more often, giving the guardrail layer more real failures to catch and demonstrate.

## Purpose

LLM agents are unreliable decision-makers but are increasingly given real actions to take (API calls, DB writes, workflow triggers). This project targets: malformed/hallucinated tool output, unauthorized actions, inconsistent handling of edge cases, and lack of visibility when agents misbehave. The agent-framework ecosystem (LangChain, LangGraph, AutoGen, CrewAI) focuses on capability, not safety - few reusable open-source libraries exist purely for constraining and proving agent behavior. The project formalizes the ad-hoc guardrail pattern built once at MatchOS into a general, measurable, open-source tool, and demonstrates production-safety instincts for interviews.

## Full Tech Stack (all free/local)

| Layer | Tool | Role |
| --- | --- | --- |
| Orchestration | LangGraph + LangChain | LangGraph = agent state machine where guardrails hook in at node boundaries (ships a GuardedNode wrapper); LangChain = LLM client plumbing (ChatOllama, prompts, parsers) |
| LLM | Ollama | Local, free. llama3 (8B, main agent) + qwen2.5:3b-instruct (weaker, to stress-test guardrails) |
| Schema validation | Pydantic | Validates every tool call/output against a defined schema before execution |
| Vector store + data store | FAISS AND local PostgreSQL/pgvector via Docker (both kept, not swapped) | FAISS for lightweight in-process demo retrieval; PostgreSQL/pgvector (free, self-hosted) for persistent storage of guardrail logs, allowlist config, and eval results - reuses MatchOS experience |
| Observability | Langfuse, self-hosted via Docker | Traces every guardrail decision (proposed to blocked/overridden) |
| Evaluation | DeepEval + Ollama as judge | Red-team dataset of malformed/off-policy prompts scored for guardrail catch rate |
| CI/CD | GitHub Actions | Runs eval suite on every push/PR; fails build if catch rate regresses |
| Packaging | pyproject.toml / setuptools | pip install -e ., drops into any LangGraph project in a few lines |

**Flow:** User query -> LangGraph node -> Guardrail wrapper intercepts output (Pydantic schema check -> allowlist check -> deterministic override check) -> Langfuse logs the decision -> validated output returned. Separately, DeepEval red-team suite runs in GitHub Actions on every push, scoring catch rate via Ollama-as-judge.

## How to Build It (v1 scope)

1. Pull local models: ollama pull llama3, ollama pull qwen2.5:3b-instruct.
2. guardrails/schemas.py - Pydantic models per tool/step; auto-reprompt once on validation failure, then fall back to a safe default.
3. guardrails/allowlist.py - config-driven list of permitted tools/functions; anything else blocked and logged.
4. guardrails/overrides.py - regex/pattern-based deterministic layer that skips the LLM entirely for known-safe inputs.
5. Wire in self-hosted Langfuse (same setup as Agent\_Eval\_Lab) for full decision tracing.
6. Build a red-team eval dataset; score guardrail catch rate with DeepEval + Ollama.
7. Add GitHub Actions CI running the eval suite on every PR.
8. Package as an installable module (pip install -e .).

## Cross-Skill Additions (cybersecurity / system design / DevOps), staged

**v1 (ship first):** core guardrails + Langfuse tracing + DeepEval red-team suite + basic GitHub Actions CI + README framed explicitly against the OWASP Top 10 for LLM Applications (schema validation -> Insecure Output Handling; allowlist -> Excessive Agency; overrides -> reduces Prompt Injection surface).

**v1.1 (fast follow):**

- Prompt-injection detection module (scans input for injection patterns before it reaches the LLM)
- SECURITY.md file describing threats defended against plus how to report issues
- GitHub Actions matrix builds testing across multiple local models in parallel
- Secrets scanning in CI (GitHub's built-in scanning or detect-secrets)

**v2 (stretch, after v1 ships):**

- Semantic caching of guardrail decisions (cache by embedding similarity, not exact match) - reduces repeated local inference cost, demonstrates system-design/caching-strategy thinking
- Architecture Considerations at Scale section in README (concurrency, cache invalidation, idempotency of guardrail checks)
- Terraform module to hypothetically provision the stack on a cloud VM - bridges GenAI + Infrastructure-as-Code
- Grafana dashboard (self-hosted, free) visualizing guardrail catch rate over time

## Update: Frontend / Presentation Layer Decisions

- Backend/AI-only is acceptable for v1, but a minimal demo UI is recommended as a v1.1 addition for stronger non-technical reviewer impact.
- **Demo UI: Chainlit** (preferred over plain Streamlit) - purpose-built for LLM/agent demos, shows intermediate reasoning steps, which fits showing guardrail decisions (proposed -> blocked/overridden -> fallback) as a visible trace. Streamlit/Gradio remain fine simpler alternatives if Chainlit is too much overhead.
- **Dashboard: Grafana** (self-hosted, free) on top of PostgreSQL logs, for catch-rate-over-time and blocked-action trends.
- **Cube.js: not recommended for this project.** It's a semantic/BI layer for multiple dashboards sharing consistent metric definitions across teams - overkill for a single project with one dashboard. Worth learning separately if moving toward data/analytics engineering later, but skip it here.
- Other optional additions discussed: Metabase (lighter alternative to Grafana), a FastAPI wrapper exposing the guardrails framework as a standalone service (v2 stretch), MkDocs Material for a published docs site via GitHub Pages (v2 stretch, nice-to-have).
- Updated staging: v1 = core guardrails + Postgres + FAISS + Langfuse + DeepEval + CI; v1.1 = Chainlit demo UI + Grafana dashboard; v2 = FastAPI service wrapper + MkDocs docs site (in addition to the previously listed v1.1/v2 items: prompt-injection detection, SECURITY.md, matrix CI, secrets scanning, semantic caching, Terraform, scale considerations).

## Update (latest)

PostgreSQL/pgvector added ALONGSIDE FAISS, not as a swap - both are kept. PostgreSQL stores guardrail logs, allowlist config, and eval results (persistent, structured); FAISS stays for lightweight in-process demo retrieval. PostgreSQL + pgvector are confirmed free/open-source, self-hosted via Docker - no paid tier involved. README.md and the architecture Word doc have been updated to reflect this.

## Broader Learning Roadmap (beyond this project)

- **Cybersecurity:** AppSec + LLM security focus - OWASP Top 10, OWASP Top 10 for LLM Apps, proper secrets management (Vault/cloud secret managers), API security, container security (Trivy/Docker Scout). Practice: TryHackMe, PortSwigger Web Security Academy.
- **System design:** real distributed-systems fundamentals, not just interview scripts - CAP theorem, message queues (Kafka/SQS), caching strategies incl. semantic caching, load balancing, DB scaling. Resource: "Designing Data-Intensive Applications" (Kleppmann) + ByteByteGo.
- **DevOps:** GitHub Actions depth, Terraform (IaC), Kubernetes basics, Prometheus+Grafana, GitOps principles.
- **Other high-value areas:** Data engineering (Airflow, data modeling for embeddings/RAG lineage); MLOps (MLflow for experiment/model tracking, drift detection, A/B testing of prompts/models); frontend basics (Streamlit/Gradio for demo UIs, React basics); testing discipline (Hypothesis property-based testing, contract testing, mutation testing); technical writing + C4 diagramming; healthcare compliance literacy (HIPAA, SOC 2) given J&J/MatchOS healthcare background.
- **Suggested priority order:** testing discipline and MLOps first (cheapest, most directly extend current skills) -> frontend basics + technical writing (cheap, high demo impact) -> data engineering -> compliance literacy (lower general transferability, high value only if staying healthcare-adjacent).

## Open Items / Not Yet Decided

- Whether to archive or merge genai\_rag\_service into genai-raga-langgraph (recommended: archive, migrate useful bits like the multi-LLM factory pattern and circuit breaker).
- Exact final repo name for the guardrails project.
- A separate, shorter project-plan doc also exists: [LLM Agent Guardrails Framework - Project Plan](https://claude.ai/artifact/JEtCpy5Qv7Y8ecsru59XPL) - a condensed project/stack/how-to-build view without the full conversation history.

## Keeping This Doc Updated

This doc is meant to be updated as the conversation continues. When starting a new chat, paste this doc's link and ask Claude to read it for context, then continue updating it as new decisions are made.
