"""
第 4 周 · 工程实现：Token 缓存（TTL + 安全边界 + 击穿保护）
================================================================
【对应知识点】文档第 4 周「Token 缓存」：Redis + TTL + 过期预留安全边界 + 缓存击穿保护

【周次学习要点】
  - 这里的 Token 是 API access_token（会过期的访问凭证），不是第 2 周 tokenization 的分词单位。
  - TTL = 官方过期时间 - 安全余量，对应你 Java 侧 expireIn - 1000 的提前续期思想。
  - 缓存击穿 = 同一时刻大量请求发现过期、同时去刷新；用 asyncio.Lock + 双重检查挡住。

【易忽略细节 / 对照文档补足】
  1. 文档只写"分布式锁"，没说单进程内存版用 asyncio.Lock 即可；完整分布式锁是第 5 周。
  2. 用 time.monotonic() 而不是 time.time()：系统时钟被调整不会污染 TTL 判定。
  3. Redis 的 SETEX 只接受整数秒，小数 TTL 要向上取整并保证至少 1 秒。
  4. 拿不到锁的并发请求必须二次检查缓存，否则仍会重复刷新。

【示例用途】被 core_mechanisms/01~03 与 engineering_demo.py 引用；
             测试见 tests/week04/test_engineering.py
"""
from __future__ import annotations

import asyncio
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class TokenInfo:
    """凭证信息：访问令牌 + 官方给出的有效期（秒）。"""

    access_token: str
    expires_in: float


class TokenBackend(Protocol):
    """存储后端协议：沿用第 1 周 Protocol 的鸭子类型模式。"""

    async def get(self, key: str) -> str | None: ...

    async def set(self, key: str, value: str, ttl: float) -> None: ...


class MemoryBackend:
    """无 Redis 服务时的内存后端，TTL 判定用单调时钟。"""

    def __init__(self) -> None:
        self._data: dict[str, tuple[str, float]] = {}

    async def get(self, key: str) -> str | None:
        item = self._data.get(key)
        if item is None:
            return None
        value, expire_at = item
        if time.monotonic() >= expire_at:
            del self._data[key]  # 惰性删除，避免后台清理线程
            return None
        return value

    async def set(self, key: str, value: str, ttl: float) -> None:
        self._data[key] = (value, time.monotonic() + ttl)


class RedisBackend:
    """真实 Redis 后端；需要本地或远程 Redis 服务，无服务时改用 MemoryBackend。"""

    def __init__(self, url: str = "redis://localhost:6379/0") -> None:
        import redis.asyncio as redis  # 延迟导入：内存模式不依赖服务

        self.client = redis.from_url(url)

    async def get(self, key: str) -> str | None:
        value = await self.client.get(key)
        if value is None:
            return None
        return value.decode() if isinstance(value, bytes) else value

    async def set(self, key: str, value: str, ttl: float) -> None:
        await self.client.set(key, value, ex=max(1, int(ttl)))  # SETEX 只接受整数秒


class TokenCache:
    """带安全边界与击穿保护的 access_token 缓存。"""

    def __init__(
        self,
        backend: TokenBackend,
        safety_margin: float = 60.0,
        cache_key: str = "access_token",
    ) -> None:
        self.backend = backend
        self.safety_margin = safety_margin
        self.cache_key = cache_key
        self._lock = asyncio.Lock()  # 单进程击穿保护；不用可变默认值
        self.fetch_count = 0  # 便于测试验证"并发只刷新一次"
        self.last_ttl: float = 0.0

    def effective_ttl(self, expires_in: float) -> float:
        """安全边界：提前 safety_margin 秒过期，余量不足时至少保留 1 秒。"""
        return max(1.0, expires_in - self.safety_margin)

    async def get_token(
        self,
        fetcher: Callable[[], Awaitable[TokenInfo]],
    ) -> str:
        """先查缓存；未命中再抢锁，抢到后二次检查，避免并发重复刷新。"""
        cached = await self.backend.get(self.cache_key)
        if cached is not None:
            return cached

        async with self._lock:
            cached = await self.backend.get(self.cache_key)  # 双重检查
            if cached is not None:
                return cached
            info = await fetcher()
            self.fetch_count += 1
            self.last_ttl = self.effective_ttl(info.expires_in)
            await self.backend.set(self.cache_key, info.access_token, self.last_ttl)
            return info.access_token
