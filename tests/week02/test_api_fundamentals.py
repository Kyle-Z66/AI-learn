"""
第 2 周单元测试 · 动作 1：9 个模型 API 原理点
================================================================
数字前缀脚本用 importlib 动态导入（同第 1 周测试写法）。
"""
from __future__ import annotations

import importlib
from typing import Any, cast

m01 = cast(Any, importlib.import_module("week02.api_fundamentals.01_tokenization"))
m02 = cast(Any, importlib.import_module("week02.api_fundamentals.02_context_window"))
m03 = cast(Any, importlib.import_module("week02.api_fundamentals.03_sampling_params"))
m04 = cast(Any, importlib.import_module("week02.api_fundamentals.04_streaming"))
m05 = cast(Any, importlib.import_module("week02.api_fundamentals.05_function_calling"))
m06 = cast(Any, importlib.import_module("week02.api_fundamentals.06_roles"))
m07 = cast(Any, importlib.import_module("week02.api_fundamentals.07_prompt_caching"))
m08 = cast(Any, importlib.import_module("week02.api_fundamentals.08_model_routing"))
m09 = cast(Any, importlib.import_module("week02.api_fundamentals.09_non_determinism"))


# 01 tokenization
def test_bpe_and_cost() -> None:
    assert m01.bpe_merge_once(list("unhappy"), ("u", "n")) == ["un", "h", "a", "p", "p", "y"]
    assert m01.bpe_merge_once(["un", "h"], ("un", "h")) == ["unh"]
    assert m01.estimate_tokens("hello") >= 1
    assert m01.estimate_cost(1000, 500, 0.01, 0.02) == 0.02


# 02 context window
def test_context_window() -> None:
    msg = m02.Message("user", "hello world")
    window = m02.ContextWindow(max_tokens=20)
    assert m02.can_fit(window, [msg], reserve_output=5) is True
    assert m02.can_fit(window, [msg], reserve_output=100) is False

    history = [m02.Message("user", f"历史{i}") for i in range(10)]
    messages = [m02.Message("system", "指令"), *history]
    trimmed = m02.trim_messages(messages, token_limit=10)
    assert trimmed[0].role == "system"
    assert len(trimmed) < len(messages)


# 03 sampling params
def test_sampling_params() -> None:
    greedy = m03.softmax_with_temperature([2.0, 1.0, 0.1], 0.0)
    assert greedy == [1.0, 0.0, 0.0]
    filtered = m03.top_p_filter([0.7, 0.2, 0.1], top_p=0.8)
    assert round(sum(filtered), 6) == 1.0
    assert "截断" in m03.check_finish_reason("length", 100)


# 04 streaming
def test_sse_parsing() -> None:
    lines = m04.build_sse_lines(["你", "好"])
    payloads = m04.parse_sse_lines(lines)
    assert len(payloads) == 2
    assert m04.parse_sse_lines(["data: [DONE]", "data: {\"x\":1}"]) == []


# 05 function calling
def test_function_calling() -> None:
    tool = m05.build_tool_schema()
    assert tool["function"]["name"] == "query_alert_count"
    decision = m05.mock_model_decision("查询告警", [tool])
    assert decision["tool_calls"] is not None
    result = m05.execute_tool("query_alert_count", '{"system_name": "orchestrator"}')
    assert "3 条" in result


# 06 roles
def test_message_roles() -> None:
    messages = m06.build_messages("系统指令", [], "用户输入")
    assert [m.role for m in messages] == ["system", "user"]


# 07 prompt caching
def test_prompt_cache() -> None:
    prefix, suffix = m07.split_cached_prefix("固定指令{{USER_INPUT}}动态")
    assert prefix == "固定指令"
    assert suffix == "动态"
    assert m07.cache_key(prefix) == m07.cache_key("固定指令")


# 08 model routing
def test_model_routing() -> None:
    available = {"deepseek-chat", "qwen-plus", "glm-4-plus"}
    assert m08.route("extract", available) == "deepseek-chat"
    assert m08.route("extract", set()) is None
    chain = m08.fallback_chain("deepseek-chat", available)
    assert chain[0] == "deepseek-chat"
    assert len(chain) == 3


# 09 non-determinism
def test_non_determinism() -> None:
    outputs = m09.sample_outputs("prompt", n=20, temperature=0.8)
    common, ratio = m09.consistency_report(outputs)
    assert common in outputs
    assert 0 < ratio <= 1
