"""
第 4 周 · 核心机制 01：Token 缓存与 TTL
================================================================
【对应知识点】文档第 4 周「Token 缓存」：Redis + TTL 缓存 access_token

【周次学习要点】
  - 本周 Token 指 API access_token（访问凭证），不是第 2 周 tokenization 的分词 token。
  - TTL 缓存的价值：避免每个请求都去认证服务换 token，省一次网络往返。
  - 后端用 Protocol 抽象（第 1 周 07_protocol.py），内存版与 Redis 版可互换。

【易忽略细节】
  1. 内存后端用 monotonic 时钟判过期，系统时间被调整不会误判。
  2. 缓存命中不会调用 fetcher；示例用 fetch_count 验证这一点。
  3. Redis 版需真实服务，无服务时用 MemoryBackend，接口完全一致。

【示例用途】可运行：`python -m week04.core_mechanisms.01_token_cache_ttl`
             （跨包引用工程层，须从仓库根以 -m 运行）
             测试见 tests/week04/test_core_mechanisms.py
"""
from __future__ import annotations

import asyncio

from week04.engineering.token_cache import MemoryBackend, TokenCache, TokenInfo


async def fetch_token() -> TokenInfo:
    """模拟调用认证服务换取访问凭证。"""
    await asyncio.sleep(0.01)
    return TokenInfo(access_token="token-alpha", expires_in=3600)


async def demo() -> None:
    cache = TokenCache(MemoryBackend(), safety_margin=60)
    first = await cache.get_token(fetch_token)
    second = await cache.get_token(fetch_token)
    print("首次获取：", first)
    print("二次获取：", second)
    print("实际刷新次数：", cache.fetch_count, "（应为 1，第二次命中缓存）")
    print("写入 TTL：", cache.last_ttl, "秒（官方 3600 - 安全余量 60）")


if __name__ == "__main__":
    asyncio.run(demo())
