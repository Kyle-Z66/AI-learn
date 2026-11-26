"""
第 10 周单元测试 · reranker / fallback / 结果模型
"""
from __future__ import annotations

import asyncio

import pytest
from week10.engineering.engineering_demo import demo
from week10.engineering.fallback import rerank_with_fallback
from week10.engineering.models import RerankCandidate, RerankResult
from week10.engineering.reranker import (
    DeterministicReranker,
    RerankerConfig,
    proper_nouns,
)

CANDIDATES = [
    RerankCandidate("d1", "断路器通用巡检流程", 0.95),
    RerankCandidate("d2", "SGCC-4012 断路器巡检周期", 0.90),
    RerankCandidate("d3", "ERR_4012 通信超时", 0.85),
]
QUERY = "SGCC-4012 断路器巡检"


def test_models_have_sensible_defaults() -> None:
    result = RerankResult(candidates=CANDIDATES[:1])
    assert not result.degraded and result.reason == ""
    assert result.scores == {}


def test_reranker_config_validation() -> None:
    with pytest.raises(ValueError, match="延迟"):
        RerankerConfig(delay_ms=-1)
    with pytest.raises(ValueError, match="并发"):
        RerankerConfig(concurrency=0)


def test_proper_nouns_extraction() -> None:
    assert proper_nouns("SGCC-4012 与 ERR_4012") == {"sgcc-4012", "err_4012"}
    assert proper_nouns("断路器巡检") == set()


def test_score_is_bounded_and_prefers_proper_noun() -> None:
    reranker = DeterministicReranker()
    score = reranker.score(QUERY, "SGCC-4012 断路器巡检周期")
    assert 0.0 <= score <= 1.0
    assert score > reranker.score(QUERY, "差旅报销标准")


async def test_rerank_orders_candidates() -> None:
    reranker = DeterministicReranker()
    scored = await reranker.rerank(QUERY, CANDIDATES)
    assert len(scored) == len(CANDIDATES)
    assert scored[0][1] >= scored[-1][1]
    assert {item.chunk_id for item, _ in scored} == {"d1", "d2", "d3"}


async def test_fallback_success_keeps_reranked_order() -> None:
    result = await rerank_with_fallback(QUERY, CANDIDATES, top_k=2)
    assert not result.degraded and result.reason == ""
    assert len(result.candidates) == 2
    assert set(result.scores) == {"d1", "d2", "d3"}


async def test_fallback_timeout_returns_stage_order() -> None:
    engine = DeterministicReranker(RerankerConfig(delay_ms=30))
    result = await rerank_with_fallback(
        QUERY, CANDIDATES, top_k=2, timeout_ms=1, reranker=engine
    )
    assert result.degraded and result.reason == "timeout"
    assert [item.chunk_id for item in result.candidates] == ["d1", "d2"]


async def test_fallback_failure_returns_stage_order() -> None:
    engine = DeterministicReranker(RerankerConfig(fail=True))
    result = await rerank_with_fallback(QUERY, CANDIDATES, top_k=2, reranker=engine)
    assert result.degraded and result.reason == "error:RuntimeError"
    assert [item.chunk_id for item in result.candidates] == ["d1", "d2"]


async def test_cancellation_is_not_swallowed() -> None:
    engine = DeterministicReranker(RerankerConfig(delay_ms=100))
    task = asyncio.create_task(
        rerank_with_fallback(QUERY, CANDIDATES, timeout_ms=10, reranker=engine)
    )
    await asyncio.sleep(0)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task


async def test_engineering_demo_runnable() -> None:
    await demo()
