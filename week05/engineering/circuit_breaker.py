"""
第 5 周 · 工程层：三态熔断器（文档标准写法的修正版）
================================================================
【对应知识点】文档第 5 周熔断器核心逻辑：closed / open / half-open 三态

【周次学习要点】
  - 熔断是"快速失败"：主模型连续失败后直接拒绝请求，不再浪费超时预算。
  - half_open 是受控探针，不是"全部放行"；成功到阈值才回到 closed。
  - 时钟与并发都做成可注入/可锁定，才能不 sleep 30 秒就完成单测。

【易忽略细节 / 对照文档补足】
  1. 文档用 time.time()：系统时间被调整会误判恢复窗口 → 换 time.monotonic()。
  2. 文档无锁：并发失败计数会丢，half_open 会被洪峰打爆 → 用 asyncio.Lock。
  3. 文档 half_open 无成功阈值：一次成功就全量恢复 → 加 success_threshold。
  4. guard() 负责成对调用 allow/record；手动调用时异常路径必须自己 record_failure。

【示例用途】被 core_mechanisms/01~03、engineering_demo 引用；
             测试见 tests/week05/test_engineering.py
"""
from __future__ import annotations

import asyncio
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from enum import StrEnum
from typing import TypeVar

T = TypeVar("T")


class BreakerState(StrEnum):
    """三态：关闭（放行）/ 打开（拒绝）/ 半开（受控探针）。"""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitOpenError(RuntimeError):
    """熔断打开时抛出：调用方应据此走降级链，而不是再打一次主模型。"""


@dataclass(frozen=True)
class BreakerConfig:
    """熔断参数。失败阈值、恢复窗口、成功阈值、半开并发探针数。"""

    failure_threshold: int = 5
    recovery_timeout: float = 30.0
    success_threshold: int = 2
    half_open_max_probes: int = 1

    def __post_init__(self) -> None:
        if self.failure_threshold < 1 or self.success_threshold < 1:
            raise ValueError("阈值必须 >= 1")
        if self.recovery_timeout <= 0 or self.half_open_max_probes < 1:
            raise ValueError("恢复时间必须 > 0，探针数必须 >= 1")


@dataclass(frozen=True)
class BreakerSnapshot:
    """供日志/测试读取的状态快照，避免直接摸内部字段。"""

    name: str
    state: str
    failures: int
    open_count: int
    probe_inflight: int


class CircuitBreaker:
    """异步安全的三态熔断器；clock 可注入，单测无需真实等待。"""

    def __init__(
        self,
        name: str,
        config: BreakerConfig | None = None,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.name = name
        self.config = config or BreakerConfig()
        self._clock = clock  # 单调时钟；注入后可精确驱动状态迁移
        self._state = BreakerState.CLOSED
        self._failures = 0
        self._successes = 0
        self._opened_at: float | None = None
        self._probe_inflight = 0
        self._lock = asyncio.Lock()
        self.open_count = 0

    @property
    def state(self) -> BreakerState:
        """读状态时惰性处理"恢复窗口已过"：open → half_open。"""
        if (
            self._state is BreakerState.OPEN
            and self._opened_at is not None
            and self._clock() - self._opened_at >= self.config.recovery_timeout
        ):
            self._state = BreakerState.HALF_OPEN
            self._successes = 0
            self._probe_inflight = 0
        return self._state

    @property
    def failure_count(self) -> int:
        return self._failures

    async def allow_request(self) -> bool:
        """closed 全放行；open 拒绝；half_open 只允许受控数量的探针。"""
        async with self._lock:
            current = self.state
            if current is BreakerState.OPEN:
                return False
            if current is BreakerState.HALF_OPEN:
                if self._probe_inflight >= self.config.half_open_max_probes:
                    return False
                self._probe_inflight += 1
            return True

    async def record_success(self) -> None:
        """成功：closed 清零失败数；half_open 累计到阈值才恢复。"""
        async with self._lock:
            if self._state is BreakerState.HALF_OPEN:
                self._probe_inflight = max(0, self._probe_inflight - 1)
                self._successes += 1
                if self._successes >= self.config.success_threshold:
                    self._close()
            elif self._state is BreakerState.CLOSED:
                self._failures = 0

    async def record_failure(self) -> None:
        """失败：closed 累加；half_open 探针失败立刻重新 open 并重置窗口。"""
        async with self._lock:
            if self._state is BreakerState.HALF_OPEN:
                self._probe_inflight = 0
                self._trip()
            elif self._state is BreakerState.CLOSED:
                self._failures += 1
                if self._failures >= self.config.failure_threshold:
                    self._trip()

    async def cancel_probe(self) -> None:
        """调用被取消时归还探针名额，避免 half_open 永久卡住。"""
        async with self._lock:
            if self._state is BreakerState.HALF_OPEN:
                self._probe_inflight = max(0, self._probe_inflight - 1)

    async def guard(self, operation: Callable[[], Awaitable[T]]) -> T:
        """推荐入口：把 allow / record 成对封装，避免调用方漏记失败。"""
        if not await self.allow_request():
            raise CircuitOpenError(f"{self.name} 熔断器已打开，拒绝请求")
        try:
            result = await operation()
        except asyncio.CancelledError:
            await self.cancel_probe()
            raise
        except Exception:
            await self.record_failure()
            raise
        await self.record_success()
        return result

    def snapshot(self) -> BreakerSnapshot:
        return BreakerSnapshot(
            name=self.name,
            state=self.state.value,
            failures=self._failures,
            open_count=self.open_count,
            probe_inflight=self._probe_inflight,
        )

    def _trip(self) -> None:
        self._state = BreakerState.OPEN
        self._opened_at = self._clock()
        self._failures = 0
        self._successes = 0
        self._probe_inflight = 0
        self.open_count += 1

    def _close(self) -> None:
        self._state = BreakerState.CLOSED
        self._opened_at = None
        self._failures = 0
        self._successes = 0
        self._probe_inflight = 0


__all__ = [
    "BreakerConfig",
    "BreakerSnapshot",
    "BreakerState",
    "CircuitBreaker",
    "CircuitOpenError",
]
