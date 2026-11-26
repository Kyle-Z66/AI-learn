"""
第 8 周单元测试 · 向量化阶段认知误区
"""
from __future__ import annotations

from week08.pitfalls.embedding_pitfalls import (
    BASE,
    demo,
    demo_dimension_mismatch,
    demo_expired_documents,
    demo_model_mismatch,
    demo_unnormalized_dot,
    expired_ids,
    mismatch_error,
    scale_effect,
)
from week08.pitfalls.extra_gotchas import (
    ANN_TRADEOFF,
    SQL_MAPPING,
    demo_ann_tradeoff,
    demo_rbac_first,
    demo_sql_mindset,
)


def test_scale_effect_only_changes_dot() -> None:
    base_dot, base_cosine = scale_effect(BASE, 1.0)
    big_dot, big_cosine = scale_effect(BASE, 10.0)
    assert big_dot > base_dot
    assert abs(big_cosine - base_cosine) < 1e-9


def test_mismatch_and_expired_filters() -> None:
    assert "维度" in mismatch_error()
    assert set(expired_ids({})) == {"c1", "c2"}
    assert expired_ids({"valid_until_after": "2026-01-01"}) == ["c1"]


def test_embedding_pitfall_demos_runnable() -> None:
    demo_unnormalized_dot()
    demo_model_mismatch()
    demo_dimension_mismatch()
    demo_expired_documents()
    demo()


def test_extra_gotchas_mapping_and_demos() -> None:
    assert len(SQL_MAPPING) == 4
    assert len(ANN_TRADEOFF) == 3
    assert any("dept_id" in expression for expression, _ in SQL_MAPPING)
    demo_sql_mindset()
    demo_rbac_first()
    demo_ann_tradeoff()
