"""
第 5 周 · 核心机制 01：熔断器三态迁移
================================================================
【对应知识点】文档第 5 周熔断器核心逻辑：closed → open → half_open → closed

【周次学习要点】
  - 熔断看的是"一段时间内的失败"，不是单次请求失败就拒绝全部流量。
  - 可注入 clock 让 30 秒恢复窗口在单测里瞬间走完。
  - guard() 保证 allow 与 record 成对出现，漏记失败会让状态永远卡在 closed。

【易忽略细节】
  1. 文档原写法用 time.time()，系统时间回拨会让熔断"永远不恢复"。
  2. 半开态需要连续成功到阈值，一次成功就全量放行仍可能二次雪崩。
  3. snapshot() 是只读快照，避免业务代码直接改内部状态。

【示例用途】可运行：`python -m week05.core_mechanisms.01_circuit_breaker_states`
             测试见 tests/week05/test_engineering.py
"""
from __future__ import annotations

from week05.engineering.circuit_breaker import (
    BreakerConfig,
    CircuitBreaker,
    CircuitOpenError,
)


async def demo() -> None:
    now = [0.0]
    breaker = CircuitBreaker(
        "qwen",
        BreakerConfig(
            failure_threshold=3,
            recovery_timeout=30.0,
            success_threshold=2,
        ),
        clock=lambda: now[0],
    )
    print("初始：", breaker.snapshot().state)

    async def fail() -> str:
        raise ConnectionError("模拟模型不可用")

    async def ok() -> str:
        return "ok"

    for _ in range(3):
        try:
            await breaker.guard(fail)
        except ConnectionError:
            continue
    print("连续 3 次失败后：", breaker.snapshot().state)

    try:
        await breaker.guard(ok)
    except CircuitOpenError as exc:
        print("熔断期间快速失败：", exc)

    now[0] = 31.0  # 推进单调时钟，跨过恢复窗口
    print("恢复窗口过后：", breaker.snapshot().state, "（探针名额 1）")
    print("第一次探针：", await breaker.guard(ok), "→", breaker.snapshot().state)
    print("第二次探针：", await breaker.guard(ok), "→", breaker.snapshot().state)


if __name__ == "__main__":
    import asyncio

    asyncio.run(demo())
