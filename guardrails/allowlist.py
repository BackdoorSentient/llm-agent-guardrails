"""Action allowlisting.

Even if a tool call passes schema validation, it should only be allowed to
execute if the tool it names is explicitly permitted. Anything outside the
allowlist is blocked and logged rather than silently ignored or executed.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

logger = logging.getLogger("guardrails.allowlist")


class ToolNotAllowedError(Exception):
    """Raised when a requested tool is not in the allowlist."""

    def __init__(self, tool_name: str, allowed: set[str]):
        self.tool_name = tool_name
        self.allowed = allowed
        super().__init__(
            f"Tool '{tool_name}' is not in the allowlist. "
            f"Allowed tools: {sorted(allowed) or '(none configured)'}"
        )


@dataclass
class Allowlist:
    """A simple, explicit set of permitted tool names.

    Usage:
        allowlist = Allowlist(["search_docs", "summarize"])
        allowlist.check("search_docs")      # OK, returns True
        allowlist.check("delete_database")  # raises ToolNotAllowedError
    """

    allowed_tools: set[str] = field(default_factory=set)

    def __init__(self, allowed_tools: list[str] | set[str] | None = None):
        self.allowed_tools = set(allowed_tools or [])

    def is_allowed(self, tool_name: str) -> bool:
        return tool_name in self.allowed_tools

    def check(self, tool_name: str) -> bool:
        """Return True if allowed; log and raise if not."""
        if self.is_allowed(tool_name):
            logger.info("ALLOWLIST: '%s' permitted", tool_name)
            return True

        logger.warning(
            "ALLOWLIST: '%s' BLOCKED (not in allowed set: %s)",
            tool_name,
            sorted(self.allowed_tools),
        )
        raise ToolNotAllowedError(tool_name, self.allowed_tools)

    def add(self, tool_name: str) -> None:
        self.allowed_tools.add(tool_name)

    def remove(self, tool_name: str) -> None:
        self.allowed_tools.discard(tool_name)