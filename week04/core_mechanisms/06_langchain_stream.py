"""
第 4 周 · 核心机制 06：LangChain 流式接入
================================================================
【对应知识点】文档第 4 周流式输出 + 第 3 周 LCEL 的连贯递进

【周次学习要点】
  - 第 3 周学会 `prompt | model | parser`；本周把 invoke 换成 stream / astream，
    编排逻辑一行都不用改——这就是统一 Runnable 协议的价值。
  - `stream()` 同步迭代，`astream()` 异步迭代；生产环境（FastAPI）用后者。
  - 第 2 周讲过首 token 延迟概念，这里不再重复，只落地接法。

【易忽略细节】
  1. 链尾接了 OutputParser 时，stream 吐的是解析后的块，不再是原始 token；
     想逐字吐给用户，应 stream 到 model 为止，parser 另外处理。
  2. `astream()` 返回异步迭代器，必须用 `async for`，不能用普通 for。
  3. FakeListChatModel 按字符切分输出，便于无 Key 验证流式链路。

【示例用途】可运行：`python -m week04.core_mechanisms.06_langchain_stream`
             测试见 tests/week04/test_core_mechanisms.py
"""
from __future__ import annotations

import asyncio

from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate


def build_chain() -> object:
    """第 3 周的 LCEL 链，原样复用；换调用方式即可流式。"""
    prompt = ChatPromptTemplate.from_messages([("human", "{question}")])
    model = FakeListChatModel(responses=["这是流式回答的内容"])
    return prompt | model | StrOutputParser()


def demo_sync_stream() -> None:
    chain = build_chain()
    print("同步 stream：", end="")
    for chunk in chain.stream({"question": "讲讲流式"}):  # type: ignore[attr-defined]
        print(chunk, end="|")
    print()


async def demo_async_stream() -> None:
    chain = build_chain()
    print("异步 astream：", end="")
    async for chunk in chain.astream({"question": "讲讲流式"}):  # type: ignore[attr-defined]
        print(chunk, end="|")
    print()


if __name__ == "__main__":
    demo_sync_stream()
    asyncio.run(demo_async_stream())
