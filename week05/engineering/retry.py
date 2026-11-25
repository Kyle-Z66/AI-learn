"""
第 5 周 · 工程层：重试策略与幂等键（指数退避 + Retry-After）
================================================================
【对应知识点】文档第 5 周「重试 + 幂等」：429/5xx/超时可重试，写操作带幂等键

【周次学习要点】
  - 重试的前提是"错误可能是暂时的"：429 / 5xx / 超时可试，400/鉴权失败不可试。
  - 指数退避必须带抖动，否则所有客户端同时重试会形成重试风暴。
  - 非幂等操作重试靠幂等键去重：键来自业务标识，不是每次都变的随机 UUID。

【易忽略细节 / 对照文档补足】
  1. 文档只说"哪些错误可重试"，没说未知异常怎么办 → 这里默认快速失败。
  2. 服务端给了 Retry-After 时以它为准，不能比它更短（否则仍会被 429）。
  3. sleep 与随机源都可注入，单测不用真的等待或依赖随机结果。
  4. 幂等去重是简化版全局锁；生产按 key 分锁并落共享存储，避免多进程重复执行。

【示例用途】被 core_mechanisms/05~07、engineering_demo 引用；
             测试见 tests/week05/test_engineering.py
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import random
import time
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass
from typing import Any, TypeVar, cast

T = TypeVar("T")
SleepFn = Callable[[float], Awaitable[None]]


class ProviderError(Exception):
    """厂商侧调用失败的基类。"""


class HttpStatusError(ProviderError):
    """带 HTTP 状态码的失败，retry_after 单位秒。"""

    def __init__(
        self,
        status_code: int,
        message: str = "",
        retry_after: float | None = None,
    ) -> None:
        super().__init__(message or f"HTTP {status_code}")
        self.status_code = status_code
        self.retry_after = retry_after


class NonRetryableError(ProviderError):
    """明确不可重试的业务错误（参数错误、鉴权失败等）。"""


@dataclass(frozen=True)
class RetryPolicy:
    """最大尝试次数、初始退避、倍数、上限、是否抖动。"""

    max_attempts: int = 3
    base_delay: float = 0.01
    multiplier: float = 2.0
    max_delay: float = 1.0
    jitter: bool = True

    def __post_init__(self) -> None:
        if self.max_attempts < 1 or self.base_delay < 0:
            raise ValueError("max_attempts 必须 >= 1，base_delay 不能为负")


def is_retryable(exc: BaseException) -> bool:
    """可重试判据：429/5xx/连接错误/超时；其余快速失败。"""
    if isinstance(exc, NonRetryableError):
        return False
    if isinstance(exc, HttpStatusError):
        return exc.status_code == 429 or exc.status_code >= 500
    return isinstance(exc, (TimeoutError, ConnectionError))


def backoff_delay(
    attempt: int,
    policy: RetryPolicy | None = None,
    *,
    rng: Callable[[], float] | None = None,
) -> float:
    """full jitter：在 [0, capped] 内均匀取，attempt 从 1 计数。"""
    policy = policy or RetryPolicy()
    capped = min(policy.max_delay, policy.base_delay * policy.multiplier ** (attempt - 1))
    if not policy.jitter:
        return capped
    source = rng or random.random
    return source() * capped


async def call_with_retry[T](
    operation: Callable[[], Awaitable[T]],
    policy: RetryPolicy | None = None,
    *,
    sleep: SleepFn = asyncio.sleep,
    rng: Callable[[], float] | None = None,
) -> T:
    """执行调用；按判据决定是否退避重试，用尽次数后抛出最后一次异常。"""
    policy = policy or RetryPolicy()
    for attempt in range(1, policy.max_attempts + 1):
        try:
            return await operation()
        except Exception as exc:
            if not is_retryable(exc) or attempt >= policy.max_attempts:
                raise
            delay = backoff_delay(attempt, policy, rng=rng)
            if isinstance(exc, HttpStatusError) and exc.retry_after is not None:
                delay = max(delay, exc.retry_after)  # 服务端指令优先
            await sleep(delay)
    raise RuntimeError("retry policy exhausted")  # pragma: no cover


def make_idempotency_key(scope: str, payload: Mapping[str, object]) -> str:
    """按业务标识生成稳定键：同一业务请求任意次重试得到同一个键。"""
    raw = json.dumps(
        {"scope": scope, "payload": payload},
        sort_keys=True,
        ensure_ascii=False,
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]


class IdempotencyGuard:
    """TTL 内同键结果复用；全局锁保证单进程内 single-flight。"""

    def __init__(
        self,
        ttl: float = 60.0,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.ttl = ttl
        self._clock = clock
        self._results: dict[str, tuple[float, Any]] = {}
        self._lock = asyncio.Lock()
        self.hits = 0

    async def run(self, key: str, operation: Callable[[], Awaitable[T]]) -> T:
        async with self._lock:
            cached = self._results.get(key)
            if cached is not None and self._clock() - cached[0] < self.ttl:
                self.hits += 1
                return cast(T, cached[1])
            result = await operation()
            self._results[key] = (self._clock(), result)
            return result


__all__ = [
    "HttpStatusError",
    "IdempotencyGuard",
    "NonRetryableError",
    "ProviderError",
    "RetryPolicy",
    "backoff_delay",
    "call_with_retry",
    "is_retryable",
    "make_idempotency_key",
]
