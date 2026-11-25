"""
第 5 周 · 核心机制 02：半开态的单探针与成功阈值
================================================================
【对应知识点】文档熔断器半开态：half_open 允许试探恢复

【周次学习要点】
  - 文档 `return True  # half_open 允许试探` 会让恢复瞬间涌进全部等待流量。
  - 正确做法：限制并发探针数 + 连续成功到阈值才 closed。
  - 探针失败要立刻重新 open 并重置恢复窗口，不能"再试几次"。

【易忽略细节】
  1. allow_request() 成功后必须配对 record_success/record_failure，否则探针名额不释放。
  2. 取消的请求要用 cancel_probe() 归还名额，避免 half_open 永久卡死。
  3. 多进程部署时探针名额要放 Redis，本例只解决单进程。

【示例用途】可运行：`python -m week05.core_mechanisms.02_half_open_probe`
             测试见 tests/week05/test_engineering.py
"""
from __future__ import annotations

import asyncio
from contextlib import suppress

from week05.engineering.circuit_breaker import BreakerConfig, CircuitBreaker


async def demo() -> None:
    now = [0.0]
    breaker = CircuitBreaker(
        "deepseek",
        BreakerConfig(
            failure_threshold=1,
            recovery_timeout=5.0,
            success_threshold=2,
            half_open_max_probes=1,
        ),
        clock=lambda: now[0],
    )

    async def fail() -> str:
        raise ConnectionError("主模型故障")

    with suppress(ConnectionError):
        await breaker.guard(fail)
    print("故障后状态：", breaker.snapshot().state)

    now[0] = 6.0
    allowed = await asyncio.gather(*(breaker.allow_request() for _ in range(5)))
    print(f"半开态 5 个并发请求，放行 {sum(allowed)} 个（文档原写法会放行 5 个）")

    await breaker.record_success()
    print("第 1 次探针成功后：", breaker.snapshot().state, "（阈值 2，仍半开）")
    if not await breaker.allow_request():
        raise RuntimeError("第一个探针成功后应可继续试探")
    await breaker.record_success()
    print("第 2 次探针成功后：", breaker.snapshot().state)

    # 失败路径：重新熔断后，半开探针失败立刻回到 open
    now[0] = 20.0
    for _ in range(breaker.config.failure_threshold):
        if await breaker.allow_request():
            await breaker.record_failure()
    print("再次连续失败后：", breaker.snapshot().state)
    now[0] = 30.0
    if await breaker.allow_request():
        await breaker.record_failure()
    print("半开探针失败后：", breaker.snapshot().state, "（窗口已重置）")


if __name__ == "__main__":
    asyncio.run(demo())
