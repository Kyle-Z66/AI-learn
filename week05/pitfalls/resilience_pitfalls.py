"""
第 5 周 · 本周特有坑：文档熔断器写法与可靠性反模式
================================================================
【对应知识点】文档第 5 周熔断器核心逻辑 + 重试/幂等要求

【周次学习要点】
  - 文档代码可以直接读懂原理，但不能直接抄进生产：时钟、并发、半开都要加固。
  - 可靠性手段用错了会放大故障：重试风暴、非幂等重复写、超时分层缺失。

【易忽略细节】
  1. time.time() 受系统时钟调整影响；单调时钟 monotonic 才适合算时间窗。
  2. 半开态全量放行 ≈ 没有熔断；必须限探针数并累计成功。
  3. 无抖动的重试会把瞬时故障变成同步洪峰。

【示例用途】可运行：`python -m week05.pitfalls.resilience_pitfalls`
             测试见 tests/week05/test_pitfalls.py
"""
from __future__ import annotations

import asyncio
import time
import uuid
from collections import Counter

from week05.engineering.retry import RetryPolicy, backoff_delay, make_idempotency_key
from week05.engineering.timeouts import (
    ConnectTimeout,
    TimeoutBudget,
    request_with_budget,
)


class DocCircuitBreaker:
    """文档原文的标准写法：故意保留，用来对照缺陷。"""

    def __init__(self, fail_threshold: int = 5, recovery_timeout: float = 30) -> None:
        self.fail_count = 0
        self.state = "closed"
        self.opened_at: float | None = None
        self.fail_threshold = fail_threshold
        self.recovery_timeout = recovery_timeout

    def allow_request(self) -> bool:
        if self.state == "closed":
            return True
        if self.state == "open":
            if self.opened_at is not None and time.time() - self.opened_at > self.recovery_timeout:
                self.state = "half_open"
                return True
            return False
        return True  # 文档原注释：half_open 允许试探 ← 缺陷所在

    def record_success(self) -> None:
        self.fail_count = 0
        self.state = "closed"

    def record_failure(self) -> None:
        self.fail_count += 1
        if self.fail_count >= self.fail_threshold:
            self.state = "open"
            self.opened_at = time.time()


def demo_doc_clock_risk() -> None:
    breaker = DocCircuitBreaker(recovery_timeout=30)
    breaker.state = "open"
    breaker.opened_at = time.time() + 100  # 模拟系统时钟回拨：时间窗被拉长
    print("系统时钟回拨后 allow_request() =", breaker.allow_request(), "→ 仍在拒绝")
    print("正确做法：用 time.monotonic()，见 engineering/circuit_breaker.py")


def demo_half_open_flood() -> None:
    breaker = DocCircuitBreaker()
    breaker.state = "half_open"
    allowed = sum(breaker.allow_request() for _ in range(50))
    print(f"文档 half_open 对 50 个并发请求放行 {allowed} 个（恢复瞬间二次雪崩）")
    print("正确做法：half_open_max_probes=1 + success_threshold=2")


def demo_retry_storm() -> None:
    """100 个客户端同时重试：无抖动落在同一时刻，有抖动被打散。"""
    no_jitter = RetryPolicy(jitter=False)
    fixed = Counter(round(backoff_delay(2, no_jitter), 3) for _ in range(100))
    jittered = Counter(round(backoff_delay(2), 1) for _ in range(100))
    print(f"无抖动：{len(fixed)} 个时间点，最大聚集 {max(fixed.values())} 个请求")
    print(f"有抖动：{len(jittered)} 个时间点，最大聚集 {max(jittered.values())} 个请求")


def demo_non_idempotent_retry() -> None:
    payload = {"user_id": "u-1", "ticket": "T-1001"}
    keys = {make_idempotency_key("order.create", {**payload, "uuid": uuid.uuid4().hex})}
    keys.add(make_idempotency_key("order.create", {**payload, "uuid": uuid.uuid4().hex}))
    stable = make_idempotency_key("order.create", payload)
    print(f"用随机 UUID 当幂等键：重试两次得到 {len(keys)} 个键 → 重复建单")
    print(f"用业务标识：重试得到同一个键 {stable[:12]}… → 可去重")


async def demo_timeout_confusion() -> None:
    budget = TimeoutBudget(connect=0.05, read=0.05, total=1.0)
    try:
        await request_with_budget(budget, 0.1, 0.0)
    except ConnectTimeout as exc:
        print("分层写法能定位阶段：", type(exc).__name__, "-", exc)
    print("只设一个总超时时，只知道'慢'，无法判断是建连还是读取")


async def demo() -> None:
    demo_doc_clock_risk()
    demo_half_open_flood()
    demo_retry_storm()
    demo_non_idempotent_retry()
    await demo_timeout_confusion()


if __name__ == "__main__":
    asyncio.run(demo())
