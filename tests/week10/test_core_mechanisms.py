"""
第 10 周单元测试 · 10 个核心机制样例均可运行，且关键函数级逻辑正确
"""
from __future__ import annotations

import importlib
import inspect
from typing import Any

from week10.engineering.models import RerankCandidate
from week10.engineering.reranker import DeterministicReranker, RerankerConfig

MODULES = (
    "01_bi_vs_cross",
    "02_rerank_score",
    "03_candidate_budget",
    "04_timeout_fallback",
    "05_breaker_reuse",
    "06_batch_rerank",
    "07_topk_selection",
    "08_latency_model",
    "09_three_way_compare",
    "10_rerank_metrics",
)


def load(name: str) -> Any:
    return importlib.import_module(f"week10.core_mechanisms.{name}")


async def test_all_core_scripts_runnable() -> None:
    for name in MODULES:
        result: Any = load(name).demo()
        if inspect.isawaitable(result):
            await result


def test_stage_comparison_table() -> None:
    rows = load("01_bi_vs_cross").stage_comparison()
    assert len(rows) == 2
    assert rows[0][0] == "bi-encoder" and rows[1][0] == "cross-encoder"


def test_rerank_score_is_deterministic_and_rewards_proper_noun() -> None:
    module = load("02_rerank_score")
    query = "SGCC-4012 断路器"
    assert module.score_pair(query, "SGCC-4012 断路器巡检") == module.score_pair(
        query, "SGCC-4012 断路器巡检"
    )
    ranked = [text for text, _ in module.rank_texts(query, module.TEXTS)]
    assert ranked[0] == "SGCC-4012 断路器巡检周期与温度阈值"


def test_candidate_budgets() -> None:
    module = load("03_candidate_budget")
    assert module.candidate_budget("interactive") == 50
    assert module.candidate_budget("batch") == 120


async def test_timeout_fallback_covers_three_branches() -> None:
    module = load("04_timeout_fallback")
    results = await module.run_scenarios()
    assert len(results) == 3
    assert not results[0].degraded
    assert [item.chunk_id for item in results[1].candidates] == ["d1", "d2"]
    assert results[1].degraded and results[1].reason == "timeout"
    assert results[2].degraded and results[2].reason.startswith("error:")


def test_breaker_state_transitions() -> None:
    module = load("05_breaker_reuse")
    clock = [100.0]
    breaker = module.RerankBreaker(failure_threshold=2, cooldown_s=1.0, clock=lambda: clock[0])
    assert breaker.allow()
    breaker.record_failure()
    breaker.record_failure()
    assert breaker.state == "open" and not breaker.allow()
    clock[0] += 1.0
    assert breaker.state == "half_open" and breaker.allow()
    breaker.record_success()
    assert breaker.state == "closed"


class _TrackingReranker(DeterministicReranker):
    """记录并发峰值的测试替身；不改变生产打分逻辑。"""

    def __init__(self, delay_ms: float) -> None:
        super().__init__(RerankerConfig(delay_ms=delay_ms))
        self.active = 0
        self.peak = 0

    async def score_async(self, query: str, text: str) -> float:
        self.active += 1
        self.peak = max(self.peak, self.active)
        await super().score_async(query, text)
        self.active -= 1
        return self.score(query, text)


async def test_batch_rerank_preserves_order_and_limits_concurrency() -> None:
    module = load("06_batch_rerank")
    engine = _TrackingReranker(delay_ms=10)
    scores = await module.batch_rerank("查询", ["a", "b", "c", "d"], 2, engine)
    assert len(scores) == 4
    assert engine.peak <= 2
    expected = [
        DeterministicReranker().score("查询", text) for text in ["a", "b", "c", "d"]
    ]
    assert scores == expected


def test_topk_selection_orders_by_rerank_score() -> None:
    module = load("07_topk_selection")
    selected = module.select_top_k(module.CANDIDATES, module.SCORES, k=3)
    assert [item.chunk_id for item in selected] == ["d3", "d4", "d2"]
    assert len(module.select_top_k(module.CANDIDATES, module.SCORES, k=99)) == 4


def test_latency_model_matches_documented_points() -> None:
    module = load("08_latency_model")
    assert module.estimate_latency_ms(50) == 310.0
    assert module.estimate_latency_ms(100) == 590.0


def test_three_way_compare_has_three_metrics() -> None:
    result = load("09_three_way_compare").three_way_compare()
    assert set(result) == {"dense", "hybrid", "hybrid_rerank"}
    assert all(0.0 <= score <= 1.0 for score in result.values())


def test_rerank_metrics_before_after() -> None:
    module = load("10_rerank_metrics")
    assert module.recall_at_k(["a", "b"], "b", 2) == 1.0
    assert module.mrr_at_k(["a", "b"], "b", 2) == 0.5
    assert module.mrr_at_k(["a"], "z", 2) == 0.0
    metrics = module.before_after()
    assert set(metrics) == {"before", "after"}
    assert metrics["after"]["mrr"] >= metrics["before"]["mrr"]


def test_rerank_candidates_are_plain_data() -> None:
    candidate = RerankCandidate("c-1", "文本", 0.8, "manual")
    assert candidate.chunk_id == "c-1" and candidate.stage_score == 0.8
