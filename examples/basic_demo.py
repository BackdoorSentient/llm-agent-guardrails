"""Minimal schema-validation slice against a local Ollama model.

Run from the repo root after `pip install -e .`:

    python examples/basic_demo.py
    python examples/basic_demo.py "python asyncio tutorial"
"""

from __future__ import annotations

import json
import os
import sys

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import ValidationError
from dotenv import load_dotenv

from guardrails.core.schemas import SearchToolCall
from guardrails.utils.json_utils import extract_json
from guardrails.utils.logging_config import setup_logging
from guardrails.services.db_service import log_decision

load_dotenv()
setup_logging()

DEFAULT_QUERY = "best local-first LLM agent frameworks"
SYSTEM_PROMPT = """You emit a single JSON object for a search tool call.
No markdown, no commentary, no extra keys.

Required shape:
{"query": "<search string>", "max_results": <positive integer>}
"""


def main() -> int:
    user_query = " ".join(sys.argv[1:]).strip() or DEFAULT_QUERY
    model = os.environ.get("OLLAMA_MODEL", "llama3")
    base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")

    print(f"Model:     {model}")
    print(f"Ollama:    {base_url}")
    print(f"User query: {user_query}")
    print("-" * 60)

    llm = ChatOllama(model=model, base_url=base_url, temperature=0, format="json")
    try:
        response = llm.invoke(
            [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(
                    content=(
                        f"Create a SearchToolCall JSON object for this user request:\n"
                        f"{user_query}\n"
                        "Use a reasonable max_results between 1 and 10."
                    )
                ),
            ]
        )
    except Exception as exc:
        print("VALIDATION: FAILED (could not reach the model)")
        print(f"Error: {exc}")
        print("Is Ollama running? Try: ollama serve   and   ollama pull llama3")
        log_decision(
            user_query=user_query, layer="schema", decision="blocked",
            reason=f"model unreachable: {exc}", model_used=model,
        )
        return 1

    raw = response.content if isinstance(response.content, str) else str(response.content)
    print("Raw model output:")
    print(raw)
    print("-" * 60)

    try:
        payload = extract_json(raw)
    except json.JSONDecodeError as exc:
        print("VALIDATION: FAILED (output is not valid JSON)")
        print(f"Parse error: {exc}")
        log_decision(
            user_query=user_query, layer="schema", decision="blocked",
            raw_model_output=raw, reason=f"invalid JSON: {exc}", model_used=model,
        )
        return 1

    print("Parsed JSON:")
    print(json.dumps(payload, indent=2))
    print("-" * 60)

    try:
        tool_call = SearchToolCall.model_validate(payload)
    except ValidationError as exc:
        print("VALIDATION: FAILED (does not match SearchToolCall)")
        print(exc)
        log_decision(
            user_query=user_query, layer="schema", decision="blocked",
            raw_model_output=raw, parsed_payload=payload,
            reason=str(exc), model_used=model,
        )
        return 1

    print("VALIDATION: PASSED")
    print(f"SearchToolCall(query={tool_call.query!r}, max_results={tool_call.max_results})")
    log_decision(
        user_query=user_query, layer="schema", decision="passed",
        raw_model_output=raw, parsed_payload=payload, model_used=model,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())