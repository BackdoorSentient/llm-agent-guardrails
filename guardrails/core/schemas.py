"""Pydantic schemas used to validate agent tool calls."""

from pydantic import BaseModel, Field
from guardrails.utils.logging_config import setup_logging
setup_logging()
from guardrails.core.allowlist import Allowlist, ToolNotAllowedError

class SearchToolCall(BaseModel):
    """Expected shape of a search tool call produced by the model."""

    query: str
    max_results: int = Field(gt=0)
