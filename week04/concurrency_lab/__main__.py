"""
第 4 周 · 动手项目入口：100 请求并发压测对比表
================================================================
【示例用途】可运行：`python -m week04.concurrency_lab`
             Mock 调用无需 API Key；可直接对照文档验收标准第 3 条。

【本周边界】只量化串行/gather/Semaphore 的吞吐差异；
             熔断、审计、可观测是第 5 周内容。
"""
from __future__ import annotations

import asyncio

from week04.concurrency_lab.benchmark import run_all
from week04.concurrency_lab.models import BenchmarkResult

COUNT = 100
DELAY = 0.01
LIMIT = 10


def print_table(results: list[BenchmarkResult]) -> None:
    """打印验收标准要求的耗时对比表。"""
    print(f"{'模式':<18}{'请求数':<10}{'耗时(ms)':<14}{'QPS':<12}{'峰值并发'}")
    for result in results:
        print(
            f"{result.mode:<18}{result.count:<10}"
            f"{result.elapsed * 1000:<14.1f}{result.qps:<12.1f}{result.peak}"
        )

    baseline = results[0].elapsed
    for result in results[1:]:
        print(f"{result.mode} 相比串行加速：{baseline / result.elapsed:.1f} 倍")


async def main() -> None:
    print(f"压测参数：{COUNT} 个请求，单次模拟延迟 {DELAY * 1000:.0f} ms")
    results = await run_all(count=COUNT, delay=DELAY, limit=LIMIT)
    print_table(results)
    print("\n结论：gather 最快但无限并发会触发厂商 429；Semaphore 是可落地的折中方案。")


if __name__ == "__main__":
    asyncio.run(main())
