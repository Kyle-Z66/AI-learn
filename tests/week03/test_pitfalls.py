"""
第 3 周单元测试 · 版本陷阱与补足要点
"""
from __future__ import annotations

import pytest
from week03.pitfalls.extra_gotchas import (
    demo_brace_escape,
    demo_cost_config,
    demo_parser_returns_dict,
)
from week03.pitfalls.langchain_pitfalls import (
    DEPRECATED,
    IMPORT_LAYERS,
    SELECTION_ROWS,
    demo_import_layers,
    demo_runnable_misconception,
    demo_selection_boundary,
    demo_version,
)


def test_deprecated_list_complete() -> None:
    assert "LLMChain" in DEPRECATED
    assert "AgentExecutor" in DEPRECATED
    assert "ConversationBufferMemory" in DEPRECATED


def test_import_layers_cover_three_packages() -> None:
    assert set(IMPORT_LAYERS) == {"langchain_core", "langchain", "langchain_community"}
    assert "优先" in IMPORT_LAYERS["langchain_core"]


def test_selection_boundary_rows() -> None:
    assert len(SELECTION_ROWS) == 5
    assert any("第 14 周" in row[2] for row in SELECTION_ROWS)


def test_pitfalls_scripts_runnable(capsys: pytest.CaptureFixture[str]) -> None:
    demo_version()
    demo_import_layers()
    demo_selection_boundary()
    demo_runnable_misconception()
    out = capsys.readouterr().out
    assert "langchain" in out
    assert "RunnableSequence" in out


def test_extra_gotchas_scripts_runnable(capsys: pytest.CaptureFixture[str]) -> None:
    demo_brace_escape()
    demo_parser_returns_dict()
    demo_cost_config()
    out = capsys.readouterr().out
    assert "{ \"ok\": true }" in out
    assert "dict" in out
