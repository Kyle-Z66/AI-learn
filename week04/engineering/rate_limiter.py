"""
第 4 周 · 工程实现：令牌桶限流器（文档标准写法的修正版）
================================================================
【对应知识点】文档第 4 周「并发控制的标准写法」：RateLimiter 令牌桶

【周次学习要点】
  - 令牌桶比固定窗口更平滑：按时间速率补充 token，允许 capacity 大小的突发。
  - 这是你 Java 侧固定窗口限流的升级版，原理一致，只是换成 asyncio 实现。
  - 并发调用 acquire() 时必须加锁，否则 token 计算会出现竞态。

【易忽略细节 / 对照文档补足】
  1. 文档写 `_lock: asyncio.Lock = None`，运行时 `async with None` 会报 TypeError；
     正确写法是 field(default_factory=asyncio.Lock, init=False)。
  2. 文档用 `asyncio.get_event_loop().time()`，在协程里应换 `get_running_loop()`。
  3. `updated_at: float = 0.0` 初值不严谨：首次调用会把历史时间全算成补充量；
     这里用 None 表示"尚未开始计时"，首次调用时初始化。
  4. 等待后不要更新 updated_at：sleep 期间正好补满 1 个 token，
     下次 acquire 立即通过——这是令牌桶的正确行为，不是 bug。

【示例用途】被 core_mechanisms/10 与 concurrency_lab 引用；
             测试见 tests/week04/test_engineering.py
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field


@dataclass
class RateLimiter:
    """按速率补充 token 的异步限流器。"""

    rate: float  # 每秒补充的 token 数
    capacity: float  # 桶容量，允许的突发量
    tokens: float = 0.0
    updated_at: float | None = None
    # 关键修正：不能写 = None，否则 async with 会拿到 None
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False, repr=False)

    async def acquire(self) -> None:
        """取一个 token；不足时按缺额等待。"""
        async with self._lock:
            now = asyncio.get_running_loop().time()
            if self.updated_at is None:
                self.updated_at = now
            self.tokens = min(
                self.capacity,
                self.tokens + (now - self.updated_at) * self.rate,
            )
            self.updated_at = now

            if self.tokens < 1:
                wait_seconds = (1 - self.tokens) / self.rate
                await asyncio.sleep(wait_seconds)
                self.tokens = 0.0  # 等待期间已补满 1 个，留给下一次调用
            else:
                self.tokens -= 1
