"""
第 8 周 · 动手项目：四项实验的可测试逻辑
================================================================
【对应知识点】文档第 8 周：相似度度量 / 标量过滤 / 持久化 / ANN 召回

【周次学习要点】
  - 四个实验共用一份语料与一个查询，差异只来自度量或过滤条件。
  - 召回基准用"候选子集模拟 ANN"，口径与 core 10 一致但实现独立。
  - 所有函数返回普通数据结构，CLI 只负责打印。

【易忽略细节】
  1. 换 metric 只是换排序口径，不能据此断言某个 embedding 更好。
  2. 持久化一致性比较的是命中 id 顺序，不是浮点分数的严格相等。
  3. 召回曲线必须包含 sample_ratio=1.0 作为参照点。

【示例用途】被 vector_lab/__main__.py 调用；测试见 tests/week08/test_vector_lab.py
"""
from __future__ import annotations

import tempfile
from pathlib import Path

from week08.engineering.embeddings import HashEmbedding
from week08.engineering.vector_store import (
    load_store,
    save_store,
    similarity,
)
from week08.vector_lab.corpus import QUERY, TODAY, build_store

METRICS = ("cosine", "dot", "euclidean")


def compare_metrics(top_k: int = 3) -> dict[str, list[str]]:
    """同一查询在三种度量下的 Top-K 命中 id。"""
    query = tuple(HashEmbedding(16).embed_query(QUERY))
    return {
        metric: [
            hit.record.id
            for hit in build_store(metric=metric).search(query, top_k=top_k)
        ]
        for metric in METRICS
    }


def scalar_filter_demo() -> tuple[list[str], list[str]]:
    """返回 (不过滤的命中, 按部门与有效期过滤后的命中)。"""
    query = tuple(HashEmbedding(16).embed_query(QUERY))
    store = build_store()
    unfiltered = [hit.record.id for hit in store.search(query, top_k=10)]
    filtered = [
        hit.record.id
        for hit in store.search(
            query,
            top_k=10,
            where={"dept_id": "ops", "valid_until_after": TODAY},
        )
    ]
    return unfiltered, filtered


def persistence_demo() -> tuple[bool, int, int]:
    """保存重载后返回 (Top-3 是否一致, 保存前条数, 重载后条数)。"""
    query = tuple(HashEmbedding(16).embed_query(QUERY))
    store = build_store()
    before = [hit.record.id for hit in store.search(query, top_k=3)]
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "vector_store.json"
        save_store(store, path)
        restored = load_store(path)
    after = [hit.record.id for hit in restored.search(query, top_k=3)]
    return before == after, len(store), len(restored)


def recall_at_k(approximate: list[str], exact: list[str], k: int) -> float:
    """近似结果对精确 Top-K 的召回率。"""
    expected = set(exact[:k])
    if not expected:
        return 0.0
    return len(set(approximate[:k]) & expected) / len(expected)


def recall_curve(top_k: int = 3) -> tuple[tuple[float, float], ...]:
    """返回 (候选占比, recall@K) 曲线，包含 1.0 参照点。"""
    store = build_store()
    query = tuple(HashEmbedding(16).embed_query(QUERY))
    exact = [hit.record.id for hit in store.search(query, top_k=top_k)]
    records = store.records()
    curve: list[tuple[float, float]] = []
    for ratio in (0.3, 0.6, 1.0):
        size = max(1, int(len(records) * ratio))
        scored = [
            (record, similarity(query, record.vector, store.metric))
            for record in records[:size]
        ]
        scored.sort(key=lambda item: (-item[1], item[0].id))
        approximate = [record.id for record, _ in scored[:top_k]]
        curve.append((ratio, recall_at_k(approximate, exact, top_k)))
    return tuple(curve)


__all__ = [
    "METRICS",
    "compare_metrics",
    "persistence_demo",
    "recall_at_k",
    "recall_curve",
    "scalar_filter_demo",
]
