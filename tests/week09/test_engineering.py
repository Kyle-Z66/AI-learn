"""
第 9 周单元测试 · 双路索引、融合与 HybridRetriever
"""
from __future__ import annotations

import pytest
from week09.engineering.bm25_index import BM25Index, tokenize
from week09.engineering.dense_index import DenseIndex, cosine_similarity
from week09.engineering.engineering_demo import DEMO_CORPUS, demo
from week09.engineering.fusion import (
    min_max_normalize,
    reciprocal_rank_fusion,
    weighted_score_fusion,
)
from week09.engineering.hybrid_retriever import HybridRetriever
from week09.engineering.models import Candidate


def test_candidate_copy_without_scores() -> None:
    original = Candidate("c-1", "文本", "src", "运维", True, 3.2, 0.8, 0.9, 1)
    copied = original.copy_without_scores()
    assert copied.chunk_id == "c-1" and copied.dept == "运维"
    assert (copied.bm25_score, copied.dense_score, copied.fused_score, copied.rank) == (
        None,
        None,
        None,
        None,
    )


def test_tokenize_is_shared_by_index_and_query() -> None:
    assert tokenize("SGCC-4012 断路器") == tokenize("sgcc-4012 断路器")
    assert "4012" in tokenize("ERR_4012 错误码")


def test_bm25_prefers_exact_proper_noun() -> None:
    corpus = [
        Candidate("a", "SGCC-4012 断路器说明", "manual"),
        Candidate("b", "SGCC-5200 断路器说明", "manual"),
        Candidate("c", "差旅报销标准", "finance"),
    ]
    assert BM25Index(corpus).search("SGCC-4012")[0][0] == "a"
    assert BM25Index(corpus).search("") == []
    assert BM25Index([]).search("任意") == []


def test_cosine_similarity_edge_cases() -> None:
    assert cosine_similarity([1.0, 0.0], [1.0, 0.0]) == pytest.approx(1.0)
    assert cosine_similarity([1.0, 0.0], [0.0, 1.0]) == pytest.approx(0.0)
    assert cosine_similarity([0.0, 0.0], [1.0, 0.0]) == 0.0
    assert cosine_similarity([1.0], [1.0, 2.0]) == 0.0


def test_dense_index_search_is_deterministic() -> None:
    corpus = [Candidate("a", "断路器巡检流程", "manual"), Candidate("b", "报销标准", "finance")]
    index = DenseIndex(corpus)
    assert index.search("断路器巡检") == index.search("断路器巡检")
    assert all(0.0 < score <= 1.0 for _, score in index.search("断路器巡检"))


def test_rrf_and_normalization() -> None:
    assert reciprocal_rank_fusion([["a", "b"], ["b", "a"]])[0] == "a"
    assert min_max_normalize({"a": 1.0, "b": 3.0}) == {"a": 0.0, "b": 1.0}
    assert min_max_normalize({"a": 2.0, "b": 2.0}) == {"a": 0.0, "b": 0.0}
    assert min_max_normalize({}) == {}


def test_weighted_fusion_and_validation() -> None:
    result = weighted_score_fusion({"a": 3.0}, {"b": 0.9}, weight_sparse=1.0)
    assert result == ["a", "b"]
    with pytest.raises(ValueError, match="权重"):
        weighted_score_fusion({"a": 1.0}, {"b": 1.0}, weight_sparse=1.2)
    with pytest.raises(ValueError, match="k"):
        reciprocal_rank_fusion([["a"]], k=0)


def test_hybrid_retriever_filters_before_recall() -> None:
    retriever = HybridRetriever(DEMO_CORPUS)
    results = retriever.retrieve("SGCC-4012 巡检", top_k=10, dept="运维")
    assert "c-04" not in {item.chunk_id for item in results}  # 失效
    assert "c-05" not in {item.chunk_id for item in results}  # 跨部门
    assert all(item.rank == index for index, item in enumerate(results, start=1))
    assert [item.chunk_id for item in results] == [
        item.chunk_id
        for item in retriever.retrieve("SGCC-4012 巡检", top_k=10, dept="运维")
    ]


def test_hybrid_retriever_modes() -> None:
    retriever = HybridRetriever(DEMO_CORPUS)
    weighted = retriever.retrieve("SGCC-4012 巡检", mode="weighted", weight_sparse=0.8)
    assert weighted and weighted[0].fused_score is not None
    with pytest.raises(ValueError, match="融合模式"):
        retriever.retrieve("SGCC-4012", mode="unknown")  # type: ignore[arg-type]


def test_engineering_demo_runnable() -> None:
    demo()
