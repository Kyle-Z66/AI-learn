"""
第 5 周 · 核心机制 06：指数退避 + 抖动 + Retry-After
================================================================
【对应知识点】文档第 5 周：指数退避重试

【周次学习要点】
  - 第 n 次退避 ≈ base × multiplier^(n-1)，再用 max_delay 封顶。
  - full jitter 在 [0, capped] 内随机，打散同时重试的客户端，避免重试风暴。
  - 服务端返回 Retry-After 时以它为准：客户端退避不能更激进。

【易忽略细节】
  1. 没有抖动时所有客户端会在同一时刻再次打爆服务。
  2. sleep 可注入，单测无需真的等待；rng 可注入，结果可复现。
  3. 退避上限防止长尾等待超过调用方总超时预算。

【示例用途】可运行：`python -m week05.core_mechanisms.06_exponential_backoff`
             测试见 tests/week05/test_engineering.py
"""
from __future__ import annotations

from week05.engineering.retry import (
    HttpStatusError,
    RetryPolicy,
    backoff_delay,
    call_with_retry,
)


async def demo() -> None:
    fixed = RetryPolicy(base_delay=0.1, multiplier=2.0, max_delay=1.0, jitter=False)
    print("无抖动退避（秒）：", [backoff_delay(i, fixed) for i in range(1, 7)])
    jittered = RetryPolicy(base_delay=0.1, multiplier=2.0, max_delay=1.0)
    print(
        "full jitter（固定 rng=0.5）：",
        [round(backoff_delay(i, jittered, rng=lambda: 0.5), 4) for i in range(1, 5)],
    )

    slept: list[float] = []

    async def fake_sleep(seconds: float) -> None:
        slept.append(seconds)

    attempts = 0

    async def flaky() -> str:
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise HttpStatusError(429, "限流", retry_after=0.7)
        return "ok"

    result = await call_with_retry(
        flaky,
        RetryPolicy(max_attempts=3, base_delay=0.01, jitter=False),
        sleep=fake_sleep,
    )
    print(f"重试结果={result} 尝试={attempts} 次 实际等待={slept}（Retry-After 优先）")


if __name__ == "__main__":
    import asyncio

    asyncio.run(demo())
