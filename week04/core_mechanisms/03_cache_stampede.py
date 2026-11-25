"""
第 4 周 · 核心机制 03：缓存击穿保护
================================================================
【对应知识点】文档第 4 周 Token 缓存：实现缓存击穿保护（分布式锁）

【周次学习要点】
  - 缓存击穿：缓存过期的瞬间，大量并发请求同时发现未命中，一起冲向认证服务。
  - 单进程用 asyncio.Lock + 双重检查即可；多进程才需要 Redis 分布式锁（SET NX EX）。
  - 这是你 Java 侧"缓存击穿加互斥锁"的直接平移。

【易忽略细节】
  1. 只加锁不够：抢到锁的请求刷新完后，等待的请求必须二次检查缓存，
     否则会排队逐个刷新（锁形同虚设）。
  2. 100 个并发请求最终应只刷新 1 次；这是验收标准里"并发击穿测试"的核心断言。
  3. 分布式锁的完整实现（过期时间、看门狗、误删防护）是第 5 周内容。

【示例用途】可运行：`python -m week04.core_mechanisms.03_cache_stampede`
             测试见 tests/week04/test_core_mechanisms.py
"""
from __future__ import annotations

import asyncio

from week04.engineering.token_cache import MemoryBackend, TokenCache, TokenInfo


async def fetch_token() -> TokenInfo:
    """模拟一次较慢的认证服务调用。"""
    await asyncio.sleep(0.05)
    return TokenInfo(access_token="token-after-refresh", expires_in=3600)


async def demo() -> None:
    cache = TokenCache(MemoryBackend(), safety_margin=60)
    results = await asyncio.gather(*(cache.get_token(fetch_token) for _ in range(100)))
    print("并发请求数：", len(results))
    print("实际刷新次数：", cache.fetch_count, "（应为 1）")
    print("返回值是否全部一致：", len(set(results)) == 1)


if __name__ == "__main__":
    asyncio.run(demo())
