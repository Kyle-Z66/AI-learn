"""
第 4 周单元测试 · 工程层：TokenCache / SSE / RateLimiter
"""
from __future__ import annotations

import asyncio

from week04.engineering.rate_limiter import RateLimiter
from week04.engineering.sse import SSEDecoder, SSEEvent, encode_sse
from week04.engineering.token_cache import MemoryBackend, TokenCache, TokenInfo


def test_effective_ttl_keeps_safety_margin() -> None:
    cache = TokenCache(MemoryBackend(), safety_margin=60)
    assert cache.effective_ttl(3600) == 3540
    assert cache.effective_ttl(30) == 1.0  # 余量大于有效期时兜底


async def test_memory_backend_ttl_expires() -> None:
    backend = MemoryBackend()
    await backend.set("token", "v", ttl=0.01)
    assert await backend.get("token") == "v"
    await asyncio.sleep(0.02)
    assert await backend.get("token") is None


async def test_token_cache_concurrent_stampede() -> None:
    """验收标准：含并发击穿测试——100 个并发只刷新一次。"""
    cache = TokenCache(MemoryBackend(), safety_margin=60)

    async def fetcher() -> TokenInfo:
        await asyncio.sleep(0.02)
        return TokenInfo("single-token", 3600)

    results = await asyncio.gather(*(cache.get_token(fetcher) for _ in range(100)))
    assert cache.fetch_count == 1
    assert set(results) == {"single-token"}


def test_sse_encoder_decoder_roundtrip() -> None:
    frame = encode_sse(SSEEvent(data="第一行\n第二行", event="delta", event_id="7"))
    assert "event: delta" in frame
    assert "id: 7" in frame
    events = SSEDecoder().feed(frame)
    assert events[0].data == "第一行\n第二行"
    assert events[0].event == "delta"


def test_sse_decoder_handles_fragments() -> None:
    """粘包：按任意碎片喂入，仍能还原完整事件。"""
    raw = encode_sse(SSEEvent(data="A")) + encode_sse(SSEEvent(data="B"))
    decoder = SSEDecoder()
    decoded: list[str] = []
    for index in range(0, len(raw), 5):
        decoded.extend(event.data for event in decoder.feed(raw[index : index + 5]))
    assert decoded == ["A", "B"]


def test_rate_limiter_uses_independent_locks() -> None:
    first = RateLimiter(rate=10, capacity=1)
    second = RateLimiter(rate=10, capacity=1)
    assert first._lock is not second._lock


async def test_rate_limiter_limits_burst() -> None:
    limiter = RateLimiter(rate=100.0, capacity=2.0)
    started = asyncio.get_running_loop().time()
    for _ in range(2):
        await limiter.acquire()
    assert asyncio.get_running_loop().time() - started < 0.05
    assert limiter.capacity == 2.0
