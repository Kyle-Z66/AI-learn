"""
第 4 周 · 动手项目：串行 / gather / Semaphore 三档压测
================================================================
【对应知识点】文档第 4 周并发压测：asyncio.gather + Semaphore 对比 100 请求

【周次学习要点】
  - 本地 Mock 异步调用模拟 LLM 网络 IO（sleep），不需要 API Key 也能量化吞吐。
  - 三档对照：串行（基线）→ 无限 gather（理论上限）→ Semaphore（生产可用）。
  - gather 无限并发虽然最快，但真实厂商会 429；Semaphore 才是可落地方案。

【易忽略细节 / 对照文档补足】
  1. 文档只说"并发 vs 串行对比"，没给第三档；补 Semaphore 档才能说明限流的代价。
  2. 峰值并发要在进入闸门后统计，否则测不到真实并发度。
  3. 每档压测都新建事件循环计时，避免前一档残留任务干扰。

【示例用途】被 __main__.py 调用；测试见 tests/week04/test_concurrency_lab.py
"""
from __future__ import annotations

import asyncio
import time

from week04.concurrency_lab.models import BenchmarkResult


class PeakTracker:
    """并发峰值计数器。"""

    def __init__(self) -> None:
        self.current = 0
        self.peak = 0

    def enter(self) -> None:
        self.current += 1
        self.peak = max(self.peak, self.current)

    def leave(self) -> None:
        self.current -= 1


async def fake_llm_call(index: int, delay: float) -> int:
    """模拟一次 LLM 调用：纯 IO 等待，无 CPU 计算。"""
    await asyncio.sleep(delay)
    return index


async def run_serial(count: int, delay: float) -> BenchmarkResult:
    """基线：逐个等待。"""
    tracker = PeakTracker()
    started = time.perf_counter()
    for index in range(count):
        tracker.enter()
        await fake_llm_call(index, delay)
        tracker.leave()
    return BenchmarkResult("串行", count, time.perf_counter() - started, tracker.peak)


async def run_gather(count: int, delay: float) -> BenchmarkResult:
    """理论上限：一次性并发全部请求。"""
    tracker = PeakTracker()

    async def tracked(index: int) -> int:
        tracker.enter()
        try:
            return await fake_llm_call(index, delay)
        finally:
            tracker.leave()

    started = time.perf_counter()
    await asyncio.gather(*(tracked(i) for i in range(count)))
    return BenchmarkResult("gather", count, time.perf_counter() - started, tracker.peak)


async def run_semaphore(count: int, delay: float, limit: int) -> BenchmarkResult:
    """生产方案：Semaphore 限制同时发起的请求数。"""
    semaphore = asyncio.Semaphore(limit)
    tracker = PeakTracker()

    async def limited(index: int) -> int:
        async with semaphore:
            tracker.enter()
            try:
                return await fake_llm_call(index, delay)
            finally:
                tracker.leave()

    started = time.perf_counter()
    await asyncio.gather(*(limited(i) for i in range(count)))
    return BenchmarkResult(
        f"Semaphore({limit})", count, time.perf_counter() - started, tracker.peak
    )


async def run_all(count: int = 100, delay: float = 0.01, limit: int = 10) -> list[BenchmarkResult]:
    """依次跑三档，返回结果列表。"""
    return [
        await run_serial(count, delay),
        await run_gather(count, delay),
        await run_semaphore(count, delay, limit),
    ]
