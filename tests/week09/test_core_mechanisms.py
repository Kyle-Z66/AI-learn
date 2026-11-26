"""
第 9 周单元测试 · 10 个核心机制样例均可运行，且关键函数级逻辑正确
"""
from __future__ import annotations

import importlib
import inspect
from typing import Any

MODULES = (
    "01_why_hybrid",
    "02_bm25_scoring",
    "03_dense_retrieval",
    "04_rrf_fusion",
    "05_weighted_fusion",
    "06_normalization_trap",
    "07_query_rewrite",
    "08_filter_and_fusion",
    "09_recall_at_k",
    "10_ablation",
)


def load(name: str) -> Any:
    return importlib.import_module(f"week09.core_mechanisms.{name}")


async def test_all_core_scripts_runnable() -> None:
    for name in MODULES:
        result: Any = load(name).demo()
        if inspect.isawaitable(result):
            await result


def test_proper_noun_collision_and_bm25_fix() -> None:
    module = load("01_why_hybrid")
    scores = module.dense_scores("SGCC-4012 断路器")
    assert scores["d1"] == scores["d2"]
    assert module.sparse_top("SGCC-4012 断路器")[0] == "d1"


def test_tokenizer_keeps_proper_nouns_and_chinese_bigrams() -> None:
    tokens = load("02_bm25_scoring").show_tokens("SGCC-4012 断路器巡检")
    assert "sgcc" in tokens and "4012" in tokens
    assert "断路" in tokens and "巡检" in tokens


def test_dense_retrieval_is_deterministic() -> None:
    module = load("03_dense_retrieval")
    assert module.dense_top("断路器巡检注意事项") == module.dense_top(
        "断路器巡检注意事项"
    )


def test_rrf_orders_by_accumulated_rank() -> None:
    module = load("04_rrf_fusion")
    assert module.merge([module.SPARSE_RANKING, module.DENSE_RANKING])[0] == "c-01"
    assert module.merge([module.SPARSE_RANKING], k=5) == module.SPARSE_RANKING[:4]


def test_weighted_fusion_weight_flips_order() -> None:
    module = load("05_weighted_fusion")
    assert module.fuse(0.8)[0] == "c-01"
    assert module.fuse(0.2)[0] == "c-02"


def test_raw_sum_is_dominated_by_bm25_scale() -> None:
    module = load("06_normalization_trap")
    raw = module.raw_sum(module.SPARSE, module.DENSE)
    normalized = module.normalized_sum(module.SPARSE, module.DENSE)
    assert raw["c-01"] > raw["c-03"]
    assert normalized["c-03"] > 0.0


def test_query_rewrite_keeps_original_and_is_idempotent() -> None:
    module = load("07_query_rewrite")
    rewritten = module.rewrite_query("SGCC-4012 怎么处理")
    assert rewritten.startswith("SGCC-4012")
    assert "国网型号 4012 断路器" in rewritten
    assert module.rewrite_query(rewritten) == rewritten


def test_filter_must_precede_fusion() -> None:
    module = load("08_filter_and_fusion")
    good = module.filter_then_fuse("SGCC-4012 巡检", top_k=3)
    bad = module.fuse_then_filter("SGCC-4012 巡检", top_k=3)
    assert len(good) == 2
    assert "f-2" not in good and "f-4" not in good
    assert len(bad) < 2


def test_recall_at_k_edge_cases() -> None:
    module = load("09_recall_at_k")
    assert module.recall_at_k(["a", "b"], {"b"}, 2) == 1.0
    assert module.recall_at_k(["a"], {"b"}, 1) == 0.0
    assert module.recall_at_k(["a"], set(), 1) == 0.0


def test_ablation_has_three_ways() -> None:
    result = load("10_ablation").ablation()
    assert set(result) == {"bm25_only", "dense_only", "hybrid_rrf"}
    assert all(0.0 <= score <= 1.0 for score in result.values())
