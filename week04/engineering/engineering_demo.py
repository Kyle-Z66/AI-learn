"""
第 4 周 · 工程规范示范：缓存 + 流式 + 限流三件套
================================================================
【对应知识点】文档第 4 周三个工作任务的工程化整合

【周次学习要点】
  - TokenCache 解决"省认证往返"，SSE 解决"首字更快"，Semaphore/RateLimiter
    解决"不打爆配额"——三者组合起来才是能扛流量的网关周边件。
  - 第 3 周的 P1 网关骨架不含这些能力，本周以增量示范形式给出，不修改 week03 代码。

【易忽略细节】
  1. 限流与 Semaphore 职责不同：前者控速率（每秒几个），后者控并发（同时几个）。
  2. Redis 后端需真实服务；本示范用内存后端，接口一致可直接替换。
  3. 熔断/审计/可观测属于第 5 周，本周不提前实现。

【示例用途】可运行：`python -m week04.engineering.engineering_demo`
             测试见 tests/week04/test_engineering.py
"""
from __future__ import annotations

import asyncio

from week04.engineering.rate_limiter import RateLimiter
from week04.engineering.sse import SSEDecoder, sse_stream
from week04.engineering.token_cache import MemoryBackend, TokenCache, TokenInfo


async def demo_token_cache() -> None:
    """100 个并发请求只刷新一次凭证。"""
    cache = TokenCache(MemoryBackend(), safety_margin=60)

    async def fetcher() -> TokenInfo:
        await asyncio.sleep(0.02)
        return TokenInfo(access_token="fresh-token", expires_in=3600)

    await asyncio.gather(*(cache.get_token(fetcher) for _ in range(100)))
    print(f"Token 缓存：100 请求 → 刷新 {cache.fetch_count} 次，TTL {cache.last_ttl:.0f} 秒")


async def demo_sse() -> None:
    """服务端逐帧 yield，客户端按帧解码。"""
    decoder = SSEDecoder()
    received: list[str] = []
    async for frame in sse_stream("流式响应", chunk_size=2, delay=0.003):
        for event in decoder.feed(frame):
            if event.event != "end":
                received.append(event.data)
    print("SSE 流式接收：", "".join(received))


async def demo_concurrency() -> None:
    """Semaphore 控并发 + RateLimiter 控速率，组合使用。"""
    semaphore = asyncio.Semaphore(5)
    limiter = RateLimiter(rate=50.0, capacity=5.0)

    async def call(index: int) -> int:
        async with semaphore:
            await limiter.acquire()  # 先过闸门，再按速率放行
            await asyncio.sleep(0.01)
            return index

    results = await asyncio.gather(*(call(i) for i in range(20)))
    print(f"并发控制：{len(results)} 个请求完成，Semaphore 上限 5，令牌桶 50/s")


async def demo() -> None:
    await demo_token_cache()
    await demo_sse()
    await demo_concurrency()


if __name__ == "__main__":
    asyncio.run(demo())
