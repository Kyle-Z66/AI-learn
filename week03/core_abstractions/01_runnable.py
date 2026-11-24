"""
第 3 周 · 核心抽象 01：Runnable（可运行协议）
================================================================
【对应知识点】文档第 3 周「LangChain 核心抽象」第 1 项：Runnable

【周次学习要点】
  - Runnable 不是能实例化的具体类，而是所有可被 LCEL 编排组件的共同协议。
  - 统一提供 invoke / ainvoke / batch / stream 等调用方式：同一段编排代码，
    换个调用方法就能从同步切到异步、流式。
  - 它对应第 1 周 07_protocol.py 的 Protocol：鸭子类型，实现协议方法即可接入。

【易忽略细节】
  1. 别写 Runnable() —— 它是协议/抽象基类，不是拿来直接创建对象的。
  2. ainvoke 是协程，必须 await；链上任一环同步阻塞，异步优势就会失效。
  3. batch 适合批量请求，stream 返回迭代器而非一次性结果。

【示例用途】可运行：`python week03/core_abstractions/01_runnable.py`
             测试见 tests/week03/test_core_abstractions.py
"""
from __future__ import annotations

import asyncio

from langchain_core.runnables import RunnableLambda


def to_upper(text: str) -> str:
    """普通函数用 RunnableLambda 包装后，就成为一个 Runnable。"""
    return text.upper()


# 包装后的对象具备 invoke / ainvoke / batch / stream 全套协议方法
upper = RunnableLambda(to_upper)


def demo_sync() -> None:
    """同步三种调用：单个、批量、流式。"""
    print("invoke :", upper.invoke("hello"))
    print("batch  :", upper.batch(["a", "b", "c"]))
    print("stream :", list(upper.stream("stream me")))


async def demo_async() -> None:
    """异步调用：沿用第 1 周的 asyncio 写法，这里不再解释事件循环。"""
    print("ainvoke:", await upper.ainvoke("hello"))
    print("abatch :", await upper.abatch(["a", "b"]))


if __name__ == "__main__":
    demo_sync()
    asyncio.run(demo_async())
