"""
第 4 周 · 核心机制 08：asyncio.Semaphore 并发控制
================================================================
【对应知识点】文档第 4 周并发压测：用 asyncio.Semaphore 实现并发控制

【周次学习要点】
  - Semaphore 是并发闸门：同时最多 N 个协程进入临界区，其余排队等待。
  - LLM 场景必配：无限 gather 会瞬间打满厂商 QPS 配额，换来一堆 429。
  - 这与你 Java 侧线程池的 corePoolSize 是同一类控制手段。

【易忽略细节】
  1. `async with semaphore` 包住的是"真正发起请求"的那段，不是整个业务函数。
  2. 信号量的值不是越大越好：要与厂商配额和目标延迟平衡。
  3. 峰值统计要在进入闸门后 +1、退出前 -1，否则测不到真实并发度。

【示例用途】可运行：`python -m week04.core_mechanisms.08_semaphore`
             测试见 tests/week04/test_core_mechanisms.py
"""
from __future__ import annotations

import asyncio
import time

TOTAL = 20
LIMIT = 4


class PeakTracker:
    """记录并发峰值，用于验证 Semaphore 确实生效。"""

    def __init__(self) -> None:
        self.current = 0
        self.peak = 0

    def enter(self) -> None:
        self.current += 1
        self.peak = max(self.peak, self.current)

    def leave(self) -> None:
        self.current -= 1


async def demo() -> None:
    semaphore = asyncio.Semaphore(LIMIT)
    tracker = PeakTracker()

    async def limited_call(index: int) -> int:
        async with semaphore:  # 闸门：最多 LIMIT 个协程同时进入
            tracker.enter()
            try:
                await asyncio.sleep(0.01)
                return index
            finally:
                tracker.leave()

    started = time.perf_counter()
    results = await asyncio.gather(*(limited_call(i) for i in range(TOTAL)))
    elapsed = time.perf_counter() - started

    print(f"请求数：{TOTAL} | 并发上限：{LIMIT}")
    print(f"实际并发峰值：{tracker.peak}（应 <= {LIMIT}）")
    print(f"总耗时：{elapsed * 1000:.1f} ms | 结果数：{len(results)}")


if __name__ == "__main__":
    asyncio.run(demo())
