"""Pydantic schemas used to validate agent tool calls."""

from pydantic import BaseModel, Field


class SearchToolCall(BaseModel):
    """Expected shape of a search tool call produced by the model."""

    query: str
    max_results: int = Field(gt=0)
