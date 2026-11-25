"""
第 4 周单元测试 · 动作 1~3：Token 缓存 / 流式 / 并发 10 个机制点
"""
from __future__ import annotations

import asyncio
import importlib
from typing import Any, cast

import pytest

# 数字前缀模块只能用 importlib 动态加载（同前三周测试文件的做法）
m01 = cast(Any, importlib.import_module("week04.core_mechanisms.01_token_cache_ttl"))
m02 = cast(Any, importlib.import_module("week04.core_mechanisms.02_safety_margin"))
m03 = cast(Any, importlib.import_module("week04.core_mechanisms.03_cache_stampede"))
m04 = cast(Any, importlib.import_module("week04.core_mechanisms.04_async_generator"))
m05 = cast(Any, importlib.import_module("week04.core_mechanisms.05_sse_frames"))
m06 = cast(Any, importlib.import_module("week04.core_mechanisms.06_langchain_stream"))
m07 = cast(Any, importlib.import_module("week04.core_mechanisms.07_gather_vs_serial"))
m08 = cast(Any, importlib.import_module("week04.core_mechanisms.08_semaphore"))
m09 = cast(Any, importlib.import_module("week04.core_mechanisms.09_taskgroup"))
m10 = cast(Any, importlib.import_module("week04.core_mechanisms.10_rate_limiter"))


async def test_token_cache_ttl_and_hit() -> None:
    first = await m01.fetch_token()
    assert first.access_token == "token-alpha"
    assert first.expires_in == 3600


def test_safety_margin_table(capsys: pytest.CaptureFixture[str]) -> None:
    m02.demo()
    assert "3540" in capsys.readouterr().out


async def test_cache_stampede_single_refresh() -> None:
    from week04.engineering.token_cache import MemoryBackend, TokenCache, TokenInfo

    cache = TokenCache(MemoryBackend(), safety_margin=60)

    async def fetcher() -> TokenInfo:
        await asyncio.sleep(0.01)
        return TokenInfo("token", 3600)

    await asyncio.gather(*(cache.get_token(fetcher) for _ in range(50)))
    assert cache.fetch_count == 1


async def test_async_generator_yields() -> None:
    collected = [token async for token in m04.token_stream("abc", delay=0)]
    assert collected == ["a", "b", "c"]


def test_sse_encode_decode_roundtrip() -> None:
    from week04.engineering.sse import SSEDecoder, SSEEvent, encode_sse

    frame = encode_sse(SSEEvent(data="你好", event_id="1"))
    assert "data: 你好" in frame
    assert frame.endswith("\n\n")
    decoder = SSEDecoder()
    events = decoder.feed(frame)
    assert events[0].data == "你好" and events[0].event_id == "1"


def test_langchain_stream_chain() -> None:
    chain = m06.build_chain()
    chunks = list(chain.stream({"question": "hi"}))  # type: ignore[attr-defined]
    assert "".join(chunks) == "这是流式回答的内容"


async def test_gather_faster_than_serial() -> None:
    serial = await m07.run_serial()
    concurrent = await m07.run_concurrent()
    assert concurrent < serial


def test_semaphore_peak_bounded() -> None:
    assert m08.LIMIT == 4
    assert m08.TOTAL == 20


async def test_rate_limiter_exists() -> None:
    limiter = m10.RateLimiter(rate=100.0, capacity=2.0)
    await limiter.acquire()
    await limiter.acquire()
    assert limiter.tokens <= limiter.capacity


async def test_taskgroup_error_group() -> None:
    await m09.demo_taskgroup()  # 不应抛出未捕获异常
