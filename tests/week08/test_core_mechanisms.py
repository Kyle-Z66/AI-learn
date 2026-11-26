"""
第 8 周单元测试 · 10 个核心机制样例函数级验证
"""
from __future__ import annotations

import importlib
from typing import Any

MODULES = (
    "01_embedding_basics",
    "02_similarity_metrics",
    "03_model_selection",
    "04_dimension_truncation",
    "05_pgvector_schema",
    "06_hnsw_ivf",
    "07_scalar_filter",
    "08_vector_store",
    "09_persistence_reload",
    "10_recall_benchmark",
)


def load(name: str) -> Any:
    return importlib.import_module(f"week08.core_mechanisms.{name}")


def test_all_core_scripts_runnable() -> None:
    for name in MODULES:
        load(name).demo()


def test_embedding_basics_profile() -> None:
    tokens, dim, norm = load("01_embedding_basics").vector_profile("SGCC-4012 超时", 16)
    assert tokens >= 3
    assert dim == 16
    assert 0.99 < norm < 1.01


def test_similarity_metrics_are_comparable() -> None:
    scores = load("02_similarity_metrics").metric_scores()
    assert set(scores) == {"cosine", "dot", "euclidean"}
    assert abs(scores["cosine"] - scores["dot"]) < 1e-9
    assert scores["euclidean"] <= 0.0


def test_model_selection_prefers_bge_for_sparse() -> None:
    module = load("03_model_selection")
    assert len(module.MODEL_CATALOG) == 3
    assert module.select_model(need_sparse=True, avoid_external_api=True) == "bge-m3"
    assert module.select_model(need_sparse=False, avoid_external_api=False)


def test_dimension_truncation_loses_information() -> None:
    module = load("04_dimension_truncation")
    assert module.truncated_norm([3.0, 4.0, 5.0], 2) == 5.0


def test_schema_checks_cover_required_fields() -> None:
    module = load("05_pgvector_schema")
    checks = module.schema_checks("embedding vector(1024) dept_id INT "
                                  "valid_until DATE metadata JSONB "
                                  "USING hnsw vector_cosine_ops")
    assert all(checks.values())


def test_index_recommendation() -> None:
    module = load("06_hnsw_ivf")
    assert len(module.INDEX_TRADEOFFS) == 3
    assert module.recommend_index(1_000, 0.99) == "精确"
    assert module.recommend_index(1_000_000, 0.98) == "HNSW"
    assert module.recommend_index(1_000_000, 0.85) == "IVF"


def test_scalar_filter_excludes_expired_and_other_dept() -> None:
    hits = load("07_scalar_filter").filtered_search("SGCC-4012 超时")
    assert "c2" not in hits
    assert "c3" not in hits
    assert hits


def test_vector_store_search_ids() -> None:
    module = load("08_vector_store")
    store = module.build_store()
    assert len(store) == 4
    assert len(module.search_ids("cosine")) == 3


def test_persistence_roundtrip_is_stable() -> None:
    before, after = load("09_persistence_reload").persistence_roundtrip()
    assert before == after
    assert before


def test_recall_at_k_and_benchmark() -> None:
    module = load("10_recall_benchmark")
    assert module.recall_at_k(["a", "b"], ["a", "c"], 2) == 0.5
    assert module.recall_at_k([], ["a"], 1) == 0.0
    curve = module.benchmark()
    assert len(curve) == 3
    assert curve[-1] == 1.0
