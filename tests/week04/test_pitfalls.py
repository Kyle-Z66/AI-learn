"""
第 4 周单元测试 · 本周特有坑与补足要点
"""
from __future__ import annotations

import asyncio

import pytest
from week04.pitfalls.concurrency_pitfalls import (
    PITFALLS,
    demo_all_pitfalls,
    demo_rate_limiter_flaw,
    demo_token_confusion,
)
from week04.pitfalls.extra_gotchas import (
    CACHE_TERMS,
    demo_cache_terms,
    demo_generator_cleanup,
    demo_sse_heartbeat,
)


def test_pitfalls_cover_token_confusion() -> None:
    assert any("Token 混淆" in name for name, _ in PITFALLS)
    assert any("TypeError" in desc for _, desc in PITFALLS)


def test_cache_terms_three_kinds() -> None:
    assert set(CACHE_TERMS) == {"击穿", "穿透", "雪崩"}


def test_pitfalls_scripts_runnable(capsys: pytest.CaptureFixture[str]) -> None:
    demo_all_pitfalls()
    asyncio.run(demo_token_confusion())
    demo_rate_limiter_flaw()
    out = capsys.readouterr().out
    assert "access_token" in out
    assert "TypeError" in out


def test_extra_gotchas_scripts_runnable(capsys: pytest.CaptureFixture[str]) -> None:
    demo_cache_terms()
    asyncio.run(demo_generator_cleanup())
    demo_sse_heartbeat()
    out = capsys.readouterr().out
    assert "雪崩" in out
    assert "心跳帧被忽略" in out
