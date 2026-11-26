"""
第 9 周 · 工程层：两路结果融合（RRF / 加权分数）
================================================================
【对应知识点】文档第 9 周：RRF（k=60，无需归一化）与加权分数融合（需先归一化）

【周次学习要点】
  - RRF 只用排名、不看原始分，两路量纲不同也能直接融合 → 默认选择。
  - 加权分数融合必须先 min-max 归一化，否则 BM25 的几分会压倒 cosine 的零点几。
  - 融合优先级：同分按 chunk_id 排序，保证多次运行顺序稳定、单测可断言。

【易忽略细节 / 对照文档补足】
  1. 文档给的 RRF 代码用 -x[1] 排序；同分时顺序不稳定，这里补 id 作为第二 key。
  2. 全部分数相等时归一化分母为 0 → 返回全 0，而不是制造 NaN。
  3. 只在一路出现的文档，另一路归一化分按 0 计，不能按"缺失即 1"处理。

【示例用途】被 hybrid_retriever.py / core_mechanisms/04、05、06 引用；
             测试见 tests/week09/test_engineering.py
"""
from __future__ import annotations

import math
from collections.abc import Mapping, Sequence


def reciprocal_rank_fusion(rankings: Sequence[Sequence[str]], k: int = 60) -> list[str]:
    """多路排名融合：score = Σ 1/(k + rank)，无需归一化各路原始分。"""
    if k <= 0:
        raise ValueError("RRF 的 k 必须 > 0")
    scores: dict[str, float] = {}
    for ranking in rankings:
        for rank, doc_id in enumerate(ranking, start=1):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank)
    return [
        doc_id
        for doc_id, _ in sorted(
            scores.items(),
            key=lambda item: (-item[1], item[0]),
        )
    ]


def min_max_normalize(scores: Mapping[str, float]) -> dict[str, float]:
    """把分数线性压到 [0, 1]；全相等时返回全 0（无区分度）。"""
    if not scores:
        return {}
    low = min(scores.values())
    high = max(scores.values())
    if math.isclose(low, high):
        return {doc_id: 0.0 for doc_id in scores}
    span = high - low
    return {doc_id: (score - low) / span for doc_id, score in scores.items()}


def weighted_score_fusion(
    sparse_scores: Mapping[str, float],
    dense_scores: Mapping[str, float],
    weight_sparse: float = 0.5,
) -> list[str]:
    """归一化后加权；只在一路出现的文档，另一路记 0 分。"""
    if not 0.0 <= weight_sparse <= 1.0:
        raise ValueError("权重必须在 [0, 1] 内")
    sparse_norm = min_max_normalize(sparse_scores)
    dense_norm = min_max_normalize(dense_scores)
    all_ids = set(sparse_scores) | set(dense_scores)
    fused = {
        doc_id: (
            weight_sparse * sparse_norm.get(doc_id, 0.0)
            + (1.0 - weight_sparse) * dense_norm.get(doc_id, 0.0)
        )
        for doc_id in all_ids
    }
    return [
        doc_id
        for doc_id, _ in sorted(
            fused.items(),
            key=lambda item: (-item[1], item[0]),
        )
    ]


__all__ = ["min_max_normalize", "reciprocal_rank_fusion", "weighted_score_fusion"]
