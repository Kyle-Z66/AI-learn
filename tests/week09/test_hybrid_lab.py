"""
第 9 周单元测试 · hybrid_lab 语料、查询与召回对比
"""
from __future__ import annotations

from week09.hybrid_lab import __main__ as lab
from week09.hybrid_lab.corpus import CORPUS, build_corpus
from week09.hybrid_lab.queries import QUERIES


def test_corpus_is_deterministic_and_copyable() -> None:
    assert len(CORPUS) == 15
    assert len({item.chunk_id for item in CORPUS}) == len(CORPUS)
    copied = build_corpus()
    copied[0].text = "改动"
    assert CORPUS[0].text != "改动"


def test_queries_cover_three_groups() -> None:
    groups = {case.group for case in QUERIES}
    assert groups == {"普通", "专名", "过滤"}
    assert all(case.relevant for case in QUERIES)
    assert all(0.0 <= lab.recall([], case.relevant, 3) <= 1.0 for case in QUERIES)


def test_recall_function_edge_cases() -> None:
    assert lab.recall(["a", "b"], frozenset({"b"}), 2) == 1.0
    assert lab.recall(["a", "b"], frozenset({"b"}), 1) == 0.0
    assert lab.recall(["a"], frozenset(), 1) == 0.0


def test_experiment_runs_all_queries() -> None:
    rows = lab.run_experiment()
    assert len(rows) == len(QUERIES)
    assert all(
        len(row.dense_top) <= lab.TOP_K and len(row.hybrid_top) <= lab.TOP_K
        for row in rows
    )
    assert all(0.0 <= row.dense_recall <= 1.0 for row in rows)
    assert all(0.0 <= row.hybrid_recall <= 1.0 for row in rows)


def test_experiment_reports_proper_noun_gain() -> None:
    rows = lab.run_experiment()
    proper = [row for row in rows if row.query_id in {"q-04", "q-05", "q-06"}]
    assert any(row.hybrid_recall >= row.dense_recall for row in proper)


def test_lab_demo_runnable() -> None:
    lab.demo()
