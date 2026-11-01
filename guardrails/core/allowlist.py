"""Action allowlisting — logic only. DB logging is injected via services."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from guardrails.services.db_service import log_decision

logger = logging.getLogger("guardrails.allowlist")


class ToolNotAllowedError(Exception):
    def __init__(self, tool_name: str, allowed: set[str]):
        self.tool_name = tool_name
        self.allowed = allowed
        super().__init__(
            f"Tool '{tool_name}' is not in the allowlist. "
            f"Allowed tools: {sorted(allowed) or '(none configured)'}"
        )


@dataclass
class Allowlist:
    allowed_tools: set[str] = field(default_factory=set)

    def __init__(self, allowed_tools: list[str] | set[str] | None = None):
        self.allowed_tools = set(allowed_tools or [])

    def is_allowed(self, tool_name: str) -> bool:
        return tool_name in self.allowed_tools

    def check(self, tool_name: str, user_query: str = "") -> bool:
        if self.is_allowed(tool_name):
            logger.info("ALLOWLIST: '%s' permitted", tool_name)
            log_decision(user_query=user_query, layer="allowlist", decision="passed", tool_name=tool_name)
            return True

        logger.warning("ALLOWLIST: '%s' BLOCKED (not in allowed set: %s)", tool_name, sorted(self.allowed_tools))
        log_decision(
            user_query=user_query, layer="allowlist", decision="blocked",
            tool_name=tool_name, reason=f"not in allowlist: {sorted(self.allowed_tools)}",
        )
        raise ToolNotAllowedError(tool_name, self.allowed_tools)

    def add(self, tool_name: str) -> None:
        self.allowed_tools.add(tool_name)

    def remove(self, tool_name: str) -> None:
        self.allowed_tools.discard(tool_name)