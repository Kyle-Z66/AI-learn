"""
第 10 周 · 核心机制 05：复用第 5 周熔断思想（轻量示意）
================================================================
【对应知识点】文档第 10 周容错设计 + 第 5 周熔断/降级链

【周次学习要点】
  - 熔断解决"rerank 已经挂了还反复打"的问题：连续失败后直接走降级。
  - 这里只做 closed / open / half-open 的状态示意，不复制 week05 的完整实现。
  - Java 侧 Redis 失败降级本地缓存、WebSocket 断连降级 List，是同一套思路。

【易忽略细节】
  1. half_open 只允许受控探针；本示意用 clock 推进窗口，不追求生产级并发控制。
  2. 时钟注入 time.monotonic：单测不用真的 sleep 到冷却结束。
  3. 熔断是"快速失败"不是"重试更多次"，别和退避重试混为一谈。

【示例用途】可运行：`python -m week10.core_mechanisms.05_breaker_reuse`
             测试见 tests/week10/test_core_mechanisms.py
"""
from __future__ import annotations

import time
from collections.abc import Callable


class RerankBreaker:
    """轻量三态熔断器：只示意状态迁移，生产请用 week05 的完整实现。"""

    def __init__(
        self,
        failure_threshold: int = 3,
        cooldown_s: float = 0.05,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if failure_threshold < 1 or cooldown_s <= 0:
            raise ValueError("阈值必须 >= 1，冷却时间必须 > 0")
        self._threshold = failure_threshold
        self._cooldown = cooldown_s
        self._clock = clock
        self._state = "closed"
        self._failures = 0
        self._opened_at: float | None = None

    @property
    def state(self) -> str:
        """惰性处理冷却窗口：open 到期后转 half_open。"""
        if (
            self._state == "open"
            and self._opened_at is not None
            and self._clock() - self._opened_at >= self._cooldown
        ):
            self._state = "half_open"
            self._failures = 0
        return self._state

    def allow(self) -> bool:
        """open 直接拒绝；closed / half_open 放行一次探针。"""
        return self.state != "open"

    def record_success(self) -> None:
        """成功即回到 closed 并清零失败数。"""
        self._state = "closed"
        self._failures = 0
        self._opened_at = None

    def record_failure(self) -> None:
        """累计到阈值即 open；探针失败立即重新打开。"""
        self._failures += 1
        if self._failures >= self._threshold:
            self._state = "open"
            self._opened_at = self._clock()
            self._failures = 0


def demo() -> None:
    breaker = RerankBreaker(failure_threshold=2)
    print(f"初始：{breaker.state}，allow={breaker.allow()}")
    breaker.record_failure()
    breaker.record_failure()
    print(f"连续两次失败：{breaker.state}，allow={breaker.allow()}")
    breaker.record_success()
    print(f"探针成功：{breaker.state}，allow={breaker.allow()}")
    print("生产链路：熔断打开 → 跳过 rerank → 直接用首阶段 Top-K")


if __name__ == "__main__":
    demo()
