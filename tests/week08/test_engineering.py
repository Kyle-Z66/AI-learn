"""
第 8 周单元测试 · 工程层：向量契约 / 本地嵌入 / 精确检索 / SQL
"""
from __future__ import annotations

import math
import tempfile
from pathlib import Path

from week08.engineering.embeddings import HashEmbedding, normalize_vector, tokenize
from week08.engineering.engineering_demo import demo
from week08.engineering.models import EmbeddingRecord, SearchHit
from week08.engineering.pgvector_sql import (
    build_create_table_sql,
    build_ivf_index_sql,
    build_search_params,
    build_search_sql,
)
from week08.engineering.vector_store import (
    InMemoryVectorStore,
    load_store,
    save_store,
    similarity,
)


def test_models_have_required_fields() -> None:
    record = EmbeddingRecord("c1", "文本", (0.1, 0.2), {"dept_id": "ops"})
    hit = SearchHit(record, 0.9)
    assert record.metadata["dept_id"] == "ops"
    assert hit.score == 0.9
    assert hit.record.id == "c1"


def test_hash_embedding_is_deterministic_and_normalized() -> None:
    for dim in (16, 1024):
        embedder = HashEmbedding(dim)
        left = embedder.embed("SGCC-4012 超时")
        right = embedder.embed("SGCC-4012 超时")
        assert len(left) == dim
        assert left == right
        assert embedder.embed_query("SGCC-4012 超时") == left
        assert abs(math.sqrt(sum(value * value for value in left)) - 1.0) < 1e-9
    raw = HashEmbedding(16, normalize=False).embed("文本")
    assert not math.isclose(sum(v * v for v in raw), 1.0)


def test_tokenize_and_normalize_edge_cases() -> None:
    assert tokenize("ERR_4012 超时") == ["err_4012", "超", "时"]
    assert normalize_vector([0.0, 0.0]) == [0.0, 0.0]
    assert normalize_vector([3.0, 4.0]) == [0.6, 0.8]


def test_similarity_metrics_and_errors() -> None:
    assert similarity([1.0, 0.0], [1.0, 0.0], "cosine") == 1.0
    assert similarity([1.0, 0.0], [0.0, 1.0], "dot") == 0.0
    assert similarity([0.0, 0.0], [1.0, 0.0], "cosine") == 0.0
    assert similarity([0.0, 0.0], [3.0, 4.0], "euclidean") == -5.0
    try:
        similarity([1.0], [1.0, 2.0])
    except ValueError:
        pass
    else:
        raise AssertionError("维度不一致应抛错")
    try:
        similarity([1.0], [1.0], "bad")
    except ValueError:
        pass
    else:
        raise AssertionError("未知度量应抛错")


def test_store_add_rejects_wrong_dimension() -> None:
    store = InMemoryVectorStore(16)
    try:
        store.add(EmbeddingRecord("bad", "文本", (0.1,)))
    except ValueError:
        pass
    else:
        raise AssertionError("维度不符应抛错")
    assert len(store) == 0


def test_store_search_filter_and_top_k() -> None:
    embedder = HashEmbedding(16)
    store = InMemoryVectorStore(16)
    for index, (text, dept, valid_until) in enumerate(
        (
            ("SGCC-4012 超时", "ops", "2030-12-31"),
            ("ERR_4012 旧流程", "ops", "2025-01-01"),
            ("SGCC-4012 权限", "dev", "2030-12-31"),
        ),
        start=1,
    ):
        store.add(
            EmbeddingRecord(
                f"c{index}",
                text,
                tuple(embedder.embed(text)),
                {"dept_id": dept, "valid_until": valid_until},
            )
        )
    query = tuple(embedder.embed_query("SGCC-4012"))
    assert all(hit.score >= store.search(query, top_k=3)[-1].score
               for hit in store.search(query, top_k=1))
    filtered = store.search(
        query,
        where={"dept_id": "ops", "valid_until_after": "2026-01-01"},
    )
    assert [hit.record.id for hit in filtered] == ["c1"]
    assert len(store.search(query, top_k=2)) == 2
    assert len(store.search(query, metric="euclidean")) == 3


def test_store_persistence() -> None:
    embedder = HashEmbedding(16)
    store = InMemoryVectorStore(16, metric="euclidean")
    store.add(EmbeddingRecord("c1", "文本", tuple(embedder.embed("文本")), {"dept_id": "ops"}))
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "store.json"
        save_store(store, path)
        restored = load_store(path)
    assert restored.dim == 16
    assert restored.metric == "euclidean"
    assert restored.records()[0].metadata == {"dept_id": "ops"}


def test_pgvector_sql_is_parameterized() -> None:
    ddl = build_create_table_sql(1024)
    assert "embedding vector(1024)" in ddl
    assert "dept_id INT" in ddl
    assert "valid_until DATE" in ddl
    assert "metadata JSONB" in ddl
    assert "vector_cosine_ops" in ddl
    assert "lists = 100" in build_ivf_index_sql()
    assert "%s::vector" in build_search_sql()
    assert build_search_params("[0.1]", 7, 50) == ("[0.1]", 7, "[0.1]", 50)


def test_engineering_demo_runnable() -> None:
    demo()
