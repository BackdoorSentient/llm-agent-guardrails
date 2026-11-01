"""Quick manual check of the allowlist layer.

Run from the repo root after `pip install -e .`:

    python examples/allowlist_demo.py
"""

from __future__ import annotations

from guardrails.utils.logging_config import setup_logging

setup_logging()

from guardrails.core.allowlist import Allowlist, ToolNotAllowedError

TEST_TOOLS = ["search_docs", "summarize", "delete_database", "send_email"]


def main() -> int:
    allowlist = Allowlist(["search_docs", "summarize"])

    print(f"Allowed tools: {sorted(allowlist.allowed_tools)}")
    print("-" * 60)

    for tool in TEST_TOOLS:
        try:
            allowlist.check(tool, user_query=f"test request for '{tool}'")
            print(f"ALLOWED : {tool}")
        except ToolNotAllowedError as exc:
            print(f"BLOCKED : {tool} -> {exc}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())