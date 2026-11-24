"""
第 3 周单元测试 · 动作 1：LangChain 五个核心抽象 + LCEL 组合原理
"""
from __future__ import annotations

import importlib
from typing import Any, cast

from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableLambda, RunnableParallel

# 数字前缀模块只能用 importlib 动态加载（同第 1/2 周测试文件的做法）
m01 = cast(Any, importlib.import_module("week03.core_abstractions.01_runnable"))
m02 = cast(Any, importlib.import_module("week03.core_abstractions.02_chat_model"))
m03 = cast(Any, importlib.import_module("week03.core_abstractions.03_prompt_template"))
m04 = cast(Any, importlib.import_module("week03.core_abstractions.04_output_parser"))
m05 = cast(Any, importlib.import_module("week03.core_abstractions.05_retriever"))
m06 = cast(Any, importlib.import_module("week03.core_abstractions.06_lcel_chain"))


def test_runnable_sync_methods() -> None:
    assert m01.upper.invoke("hi") == "HI"
    assert m01.upper.batch(["a", "b"]) == ["A", "B"]
    assert list(m01.upper.stream("x")) == ["X"]


async def test_runnable_async_methods() -> None:
    assert await m01.upper.ainvoke("hi") == "HI"
    assert await m01.upper.abatch(["a", "b"]) == ["A", "B"]


def test_chat_model_fake_no_key() -> None:
    model = m02.build_fake_model()
    response = model.invoke([HumanMessage(content="网关是干什么的？")])
    assert "网关" in response.content


def test_prompt_template_render_and_escape() -> None:
    messages = m03.build_chat_prompt().format_messages(
        system_name="cyclone", question="如何限流？"
    )
    assert messages[0].type == "system"
    assert "cyclone" in messages[0].content
    assert '"ok": true' in messages[1].content  # {{ }} 渲染成字面花括号


def test_output_parser_reuses_week02_schema() -> None:
    parsed = m04.parser.parse('{"system_name": "isc", "severity": 3, "affected_users": 50}')
    assert parsed["severity"] == 3
    assert parsed["system_name"] == "isc"


def test_retriever_interface_only() -> None:
    retriever = m05.build_retriever()
    docs = retriever.invoke("网关")
    assert [doc.metadata["id"] for doc in docs] == [1]
    assert retriever.invoke("不存在的词") == []


def test_lcel_chain_builds_sequence() -> None:
    chain = m06.build_chain()
    assert type(chain).__name__ == "RunnableSequence"
    result = chain.invoke({"text": "isc 故障，级别 2，影响 8 人"})
    assert result["system_name"] == "isc"


def test_runnable_parallel_broadcasts_input() -> None:
    parallel = RunnableParallel(
        前缀=RunnableLambda(m06.add_prefix),
        后缀=RunnableLambda(m06.add_suffix),
    )
    assert parallel.invoke("x") == {"前缀": "前缀-x", "后缀": "x-后缀"}


async def test_lcel_chain_ainvoke() -> None:
    chain = m06.build_chain()
    result = await chain.ainvoke({"text": "isc 故障，级别 2，影响 8 人"})
    assert result["severity"] == 2
