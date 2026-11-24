"""
第 3 周 · 核心抽象 06：LCEL 组合原理（本周关键原理）
================================================================
【对应知识点】文档第 3 周「LangChain 核心抽象」的串联原理（文档未单列，本工程补足）

【周次学习要点】
  - LCEL（LangChain Expression Language）解释了 5 个抽象为什么能像乐高一样拼起来。
  - 管道符 | 不是语法糖：它真的构造出一个 RunnableSequence 新对象，把上游输出喂给下游。
  - 三种组合子：串行 |（RunnableSequence）、并行 RunnableParallel、
    任意逻辑 RunnableLambda（把普通函数包成 Runnable）。
  - 同一条链换调用方法即可切同步/异步/流式：invoke / ainvoke / stream。

【易忽略细节】
  1. | 两侧必须都是 Runnable；字符串或 dict 要用 RunnableLambda 包装才能入链。
  2. ainvoke 链上任一环同步阻塞，异步优势就会失效（第 4 周并发时集中体现）。
  3. RunnableParallel 的输入会广播给每个分支，输出是 dict。
  4. 流式响应属第 4 周范围，本周只观察接口存在，不展开。

【示例用途】可运行：`python -m week03.core_abstractions.06_lcel_chain`
             （复用了第 2 周模块，须从仓库根以 -m 运行；同第 2 周 pitfalls 的做法）
             测试见 tests/week03/test_core_abstractions.py
"""
from __future__ import annotations

import asyncio
from typing import Any

from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableLambda, RunnableParallel
from week02.structured_output.models import TicketExtract


def build_chain() -> Runnable[Any, Any]:
    """一条标准 LCEL 链：PromptTemplate | ChatModel | OutputParser。"""
    prompt = ChatPromptTemplate.from_messages([
        ("human", "抽取报障信息，只返回 JSON：{text}"),
    ])
    fake_response = '{"system_name": "isc", "severity": 2, "affected_users": 8}'
    model = FakeListChatModel(responses=[fake_response, fake_response])
    parser = JsonOutputParser(pydantic_object=TicketExtract)
    chain = prompt | model | parser
    print("chain 类型：", type(chain).__name__)  # RunnableSequence
    return chain


def add_prefix(text: str) -> str:
    return f"前缀-{text}"


def add_suffix(text: str) -> str:
    return f"{text}-后缀"


def demo_combinators() -> None:
    """并行组合：输入广播给两个分支，输出汇总为 dict。"""
    parallel = RunnableParallel(
        左=RunnableLambda(add_prefix),
        右=RunnableLambda(add_suffix),
    )
    print("并行组合：", parallel.invoke("hello"))


async def demo_async(chain: Runnable[Any, Any]) -> None:
    """同一条链换 ainvoke 即可异步调用，无需改写编排逻辑。"""
    result = await chain.ainvoke({"text": "isc 故障，级别 2，影响 8 人"})
    print("ainvoke：", result)


if __name__ == "__main__":
    chain = build_chain()
    print("invoke ：", chain.invoke({"text": "isc 故障，级别 2，影响 8 人"}))
    demo_combinators()
    asyncio.run(demo_async(chain))
