"""
第 4 周 · 核心机制 07：asyncio.gather 并发 vs 串行
================================================================
【对应知识点】文档第 4 周并发压测：asyncio.gather + 并发 vs 串行对比

【周次学习要点】
  - gather 把一批协程并发调度，总耗时约等于最慢的那个，而不是所有之和。
  - LLM 调用是 IO 密集型（等网络），并发收益极大——这正是第 1 周攻 asyncio 的回报。
  - 本周只做小样本原理演示，100 请求的量化对比表在 concurrency_lab/。

【易忽略细节】
  1. gather 接收的是协程对象或 Task，不是已运行的 futures 列表。
  2. 默认 `return_exceptions=False`：任一协程抛异常会立即向外传播。
  3. 并发数不能无限放大，厂商配额会打满 → 见 08_semaphore.py。

【示例用途】可运行：`python -m week04.core_mechanisms.07_gather_vs_serial`
             测试见 tests/week04/test_core_mechanisms.py
"""
from __future__ import annotations

import asyncio
import time

REQUESTS = 20
DELAY = 0.01  # 模拟一次 LLM 网络往返


async def fake_llm_call(index: int) -> int:
    await asyncio.sleep(DELAY)
    return index


async def run_serial() -> float:
    started = time.perf_counter()
    for index in range(REQUESTS):
        await fake_llm_call(index)
    return time.perf_counter() - started


async def run_concurrent() -> float:
    started = time.perf_counter()
    await asyncio.gather(*(fake_llm_call(index) for index in range(REQUESTS)))
    return time.perf_counter() - started


async def demo() -> None:
    serial = await run_serial()
    concurrent = await run_concurrent()
    print(f"串行 {REQUESTS} 次：{serial * 1000:.1f} ms")
    print(f"gather 并发：{concurrent * 1000:.1f} ms")
    print(f"加速比：{serial / concurrent:.1f} 倍")


if __name__ == "__main__":
    asyncio.run(demo())
