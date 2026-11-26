"""
第 8 周单元测试 · 动手项目：相似度 / 过滤 / 持久化 / 召回
"""
from __future__ import annotations

from week08.vector_lab.__main__ import main
from week08.vector_lab.benchmark import (
    METRICS,
    compare_metrics,
    persistence_demo,
    recall_at_k,
    recall_curve,
    scalar_filter_demo,
)
from week08.vector_lab.corpus import LAB_ITEMS, QUERY, TODAY, build_store


def test_corpus_has_business_filter_fields() -> None:
    assert len(LAB_ITEMS) == 10
    assert any("ERR_4012" in item.text for item in LAB_ITEMS)
    assert any(item.valid_until < TODAY for item in LAB_ITEMS)
    assert len({item.dept_id for item in LAB_ITEMS}) >= 3
    assert "SGCC-4012" in QUERY
    assert len(build_store()) == 10


def test_compare_metrics_covers_three_metrics() -> None:
    results = compare_metrics()
    assert set(results) == set(METRICS)
    assert all(len(hits) == 3 for hits in results.values())


def test_scalar_filter_removes_expired_and_other_departments() -> None:
    unfiltered, filtered = scalar_filter_demo()
    assert len(unfiltered) == 10
    assert "c006" not in filtered
    assert all(item.dept_id == "ops" or item.doc_id not in filtered for item in LAB_ITEMS)
    assert filtered


def test_persistence_demo_keeps_top_hits() -> None:
    consistent, before, after = persistence_demo()
    assert consistent is True
    assert before == after == 10


def test_recall_curve_and_helper() -> None:
    assert recall_at_k(["a", "b"], ["a", "c"], 2) == 0.5
    curve = recall_curve()
    assert [ratio for ratio, _ in curve] == [0.3, 0.6, 1.0]
    assert curve[-1][1] == 1.0
    assert all(0.0 <= recall <= 1.0 for _, recall in curve)


def test_lab_cli_runnable() -> None:
    main()
