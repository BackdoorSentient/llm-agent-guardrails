import pytest
from pydantic import ValidationError

from guardrails.core.schemas import SearchToolCall


def test_valid_payload_passes():
    tool_call = SearchToolCall(query="test query", max_results=5)
    assert tool_call.query == "test query"
    assert tool_call.max_results == 5


def test_negative_max_results_fails():
    with pytest.raises(ValidationError):
        SearchToolCall(query="test query", max_results=-1)


def test_zero_max_results_fails():
    with pytest.raises(ValidationError):
        SearchToolCall(query="test query", max_results=0)