"""
第 4 周 · 核心机制 04：async 生成器与 yield
================================================================
【对应知识点】文档第 4 周流式输出：理解 async 生成器 yield 的用法

【周次学习要点】
  - async 生成器 = 能 `await` 的迭代器：用 `yield` 逐块产出，用 `async for` 消费。
  - 它与第 1 周学的协程不同：协程一次返回一个结果，生成器可以持续吐多个。
  - 流式接口（SSE / LangChain astream）底层都是这个东西。

【易忽略细节】
  1. `yield` 之后的代码在下次 `async for` 取值时才执行，是惰性产出。
  2. 提前 `break` 后要调用 `aclose()`，否则生成器资源不释放。
  3. 生成器函数体里可以 `await`，但不能用 `return value` 返回结果（StopAsyncIteration）。

【示例用途】可运行：`python -m week04.core_mechanisms.04_async_generator`
             测试见 tests/week04/test_core_mechanisms.py
"""
from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator


async def token_stream(text: str, delay: float = 0.01) -> AsyncGenerator[str, None]:
    """模拟模型逐字产出：每次 yield 一个字符后才继续下一轮。"""
    for char in text:
        await asyncio.sleep(delay)  # 模拟网络/推理耗时
        yield char


async def demo() -> None:
    print("完整消费：")
    async for token in token_stream("流式输出"):
        print(token, end="|")
    print()

    print("提前关闭：")
    generator = token_stream("abcdef")
    first = await anext(generator)
    await generator.aclose()  # 用完就关，别等 GC
    print("只取了第一个字符：", first)


if __name__ == "__main__":
    asyncio.run(demo())
