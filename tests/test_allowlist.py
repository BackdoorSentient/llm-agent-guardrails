import pytest

from guardrails.core.allowlist import Allowlist, ToolNotAllowedError


def test_allowed_tool_passes():
    allowlist = Allowlist(["search_docs"])
    assert allowlist.check("search_docs") is True


def test_disallowed_tool_raises():
    allowlist = Allowlist(["search_docs"])
    with pytest.raises(ToolNotAllowedError):
        allowlist.check("delete_database")


def test_is_allowed_does_not_raise():
    allowlist = Allowlist(["search_docs"])
    assert allowlist.is_allowed("search_docs") is True
    assert allowlist.is_allowed("delete_database") is False