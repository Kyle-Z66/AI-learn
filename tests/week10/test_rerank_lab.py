"""
第 10 周单元测试 · rerank_lab 语料、查询与三方对比
"""
from __future__ import annotations

from week10.rerank_lab import __main__ as lab
from week10.rerank_lab.corpus import CORPUS, QUERIES, build_corpus


def test_corpus_is_deterministic_and_copyable() -> None:
    assert len(CORPUS) == 15
    assert len({item.chunk_id for item in CORPUS}) == len(CORPUS)
    copied = build_corpus()
    copied[0].text = "改动"
    assert CORPUS[0].text != "改动"


def test_queries_have_relevant_annotations() -> None:
    assert len(QUERIES) == 6
    assert all(case.relevant for case in QUERIES)
    assert len({case.query_id for case in QUERIES}) == len(QUERIES)


def test_recall_and_mrr_functions() -> None:
    assert lab.recall_at_k(["a", "b"], "b", 2) == 1.0
    assert lab.recall_at_k(["a"], "b", 2) == 0.0
    assert lab.mrr_at_k(["a", "b"], "b", 2) == 0.5
    assert lab.mrr_at_k(["a"], "z", 2) == 0.0


def test_experiment_runs_all_queries_with_top_k() -> None:
    rows = lab.run_experiment(candidate_budget=10, top_k=5)
    assert len(rows) == len(QUERIES)
    assert all(len(row.dense_top) <= 5 for row in rows)
    assert all(len(row.hybrid_top) <= 5 for row in rows)
    assert all(len(row.rerank_top) <= 5 for row in rows)
    assert all(0.0 <= score <= 1.0 for row in rows for score in row.recall.values())
    assert all(0.0 <= score <= 1.0 for row in rows for score in row.mrr.values())


def test_default_budget_is_50() -> None:
    assert lab.CANDIDATE_BUDGET == 50
    assert lab.TOP_K == 5


def test_lab_demo_runnable() -> None:
    lab.demo()
