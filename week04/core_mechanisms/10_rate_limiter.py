"""
第 4 周 · 核心机制 10：令牌桶限流（文档标准写法修正版）
================================================================
【对应知识点】文档第 4 周「并发控制的标准写法」RateLimiter 代码块

【周次学习要点】
  - 令牌桶按 rate 速率补充 token，允许 capacity 大小的突发，比固定窗口更平滑。
  - 这是你 Java 侧固定窗口限流的升级版，原理一致，实现换成 asyncio。
  - 修正文档代码块里的两处缺陷，细节见 engineering/rate_limiter.py 头部说明。

【易忽略细节】
  1. 文档原写法 `_lock: asyncio.Lock = None` 会让 `async with` 报 TypeError；
     必须用 field(default_factory=asyncio.Lock, init=False)。
  2. 文档原写法 `get_event_loop().time()` 在协程里应换 `get_running_loop()`。
  3. 前 capacity 个请求立即通过，之后按 rate 匀速放行；等待期间不重置计时基准。

【示例用途】可运行：`python -m week04.core_mechanisms.10_rate_limiter`
             测试见 tests/week04/test_core_mechanisms.py
"""
from __future__ import annotations

import asyncio

from week04.engineering.rate_limiter import RateLimiter


async def demo() -> None:
    limiter = RateLimiter(rate=20.0, capacity=2.0)
    loop = asyncio.get_running_loop()
    first_at: float | None = None

    for index in range(5):
        await limiter.acquire()
        now = loop.time()
        if first_at is None:
            first_at = now  # 以第一次通过为基准，避免把进程启动开销算进来
        print(f"第 {index + 1} 次获取 token：{(now - first_at) * 1000:6.1f} ms")

    print("规律：前 2 次（桶容量）立即通过，后续按 20 token/s 匀速放行。")


if __name__ == "__main__":
    asyncio.run(demo())
