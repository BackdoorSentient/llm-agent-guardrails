"""Quick manual check of the allowlist layer."""

from guardrails.allowlist import Allowlist, ToolNotAllowedError

allowlist = Allowlist(["search_docs", "summarize"])

for tool in ["search_docs", "summarize", "delete_database", "send_email"]:
    try:
        allowlist.check(tool)
        print(f"ALLOWED : {tool}")
    except ToolNotAllowedError as exc:
        print(f"BLOCKED : {tool} -> {exc}")