"""Minimal schema-validation slice against a local Ollama model.

Run from the repo root after `pip install -e .`:

    python examples/basic_demo.py
    python examples/basic_demo.py "python asyncio tutorial"
"""

from __future__ import annotations

import json
import os
import re
import sys

# from langchain_community.chat_models import ChatOllama
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import ValidationError

from guardrails.schemas import SearchToolCall

from dotenv import load_dotenv
load_dotenv()

DEFAULT_QUERY = "best local-first LLM agent frameworks"
SYSTEM_PROMPT = """You emit a single JSON object for a search tool call.
No markdown, no commentary, no extra keys.

Required shape:
{"query": "<search string>", "max_results": <positive integer>}
"""


def extract_json(raw: str) -> dict:
    """Parse JSON from model output, including fenced ```json blocks."""
    text = raw.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.DOTALL)
    if fenced:
        text = fenced.group(1)
    else:
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end != -1 and end > start:
            text = text[start : end + 1]
    return json.loads(text)


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
        return 1

    print("Parsed JSON:")
    print(json.dumps(payload, indent=2))
    print("-" * 60)

    try:
        tool_call = SearchToolCall.model_validate(payload)
    except ValidationError as exc:
        print("VALIDATION: FAILED (does not match SearchToolCall)")
        print(exc)
        return 1

    print("VALIDATION: PASSED")
    print(f"SearchToolCall(query={tool_call.query!r}, max_results={tool_call.max_results})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
