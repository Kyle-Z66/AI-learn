"""
第 9 周 · 工程层：HybridRetriever（过滤 → 双路召回 → 融合 → Top-K）
================================================================
【对应知识点】文档第 9 周：实现双路召回，RRF 融合，输出 Top-50 候选

【周次学习要点】
  - 顺序不可换：先按 dept / valid 过滤，再建两路索引，最后融合。
  - BM25 与向量各自独立评分，融合阶段才比较；两路原始分不直接相加。
  - 返回的是带 rank / fused_score 的新 Candidate，原始语料不被污染。

【易忽略细节 / 对照文档补足】
  1. 文档没强调过滤时机：融合后再过滤会出现"Top-K 少一条"且漏掉本应补位的文档。
  2. 每路召回先取足够多的候选（默认 50），否则融合阶段可选择面太窄。
  3. mode 只允许 rrf / weighted，拼错应显式报错，别静默退化成其中一种。

【示例用途】被 engineering_demo.py / hybrid_lab/__main__.py 引用；
             测试见 tests/week09/test_engineering.py
"""
from __future__ import annotations

from typing import Literal

from week09.engineering.bm25_index import BM25Index
from week09.engineering.dense_index import DenseIndex
from week09.engineering.fusion import (
    min_max_normalize,
    reciprocal_rank_fusion,
    weighted_score_fusion,
)
from week09.engineering.models import Candidate

FusionMode = Literal["rrf", "weighted"]


class HybridRetriever:
    """双路召回 + 融合；过滤条件在两路召回之前生效。"""

    def __init__(
        self,
        candidates: list[Candidate],
        rrf_k: int = 60,
        per_path_top_k: int = 50,
    ) -> None:
        self._corpus = list(candidates)
        self._k = rrf_k
        self._per_path_top_k = per_path_top_k

    def retrieve(
        self,
        query: str,
        top_k: int = 10,
        dept: str | None = None,
        valid_only: bool = True,
        mode: FusionMode = "rrf",
        weight_sparse: float = 0.5,
    ) -> list[Candidate]:
        """执行过滤 → 双路召回 → 融合 → Top-K，返回带排名的候选。"""
        pool = self._filter(dept, valid_only)
        sparse_scores = BM25Index(pool).score_map(query)
        dense_scores = DenseIndex(pool).score_map(query)
        sparse_ranking = self._ranking(sparse_scores)
        dense_ranking = self._ranking(dense_scores)

        if mode == "rrf":
            ordered_ids = reciprocal_rank_fusion(
                [sparse_ranking, dense_ranking],
                k=self._k,
            )
            fused_scores = self._rrf_scores([sparse_ranking, dense_ranking])
        elif mode == "weighted":
            ordered_ids = weighted_score_fusion(
                sparse_scores,
                dense_scores,
                weight_sparse=weight_sparse,
            )
            sparse_norm = min_max_normalize(sparse_scores)
            dense_norm = min_max_normalize(dense_scores)
            fused_scores = {
                doc_id: (
                    weight_sparse * sparse_norm.get(doc_id, 0.0)
                    + (1.0 - weight_sparse) * dense_norm.get(doc_id, 0.0)
                )
                for doc_id in ordered_ids
            }
        else:
            raise ValueError(f"未知融合模式：{mode}")

        by_id = {candidate.chunk_id: candidate for candidate in pool}
        results: list[Candidate] = []
        for rank, doc_id in enumerate(ordered_ids[:top_k], start=1):
            item = by_id[doc_id].copy_without_scores()
            item.bm25_score = sparse_scores.get(doc_id)
            item.dense_score = dense_scores.get(doc_id)
            item.fused_score = fused_scores.get(doc_id)
            item.rank = rank
            results.append(item)
        return results

    def _filter(self, dept: str | None, valid_only: bool) -> list[Candidate]:
        """过滤必须在建索引之前完成，否则失效/越权文档会进入融合池。"""
        return [
            candidate
            for candidate in self._corpus
            if (not valid_only or candidate.valid)
            and (dept is None or candidate.dept == dept)
        ]

    def _ranking(self, scores: dict[str, float]) -> list[str]:
        """分数降序、同分按 id 排序的 chunk_id 列表。"""
        ordered = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
        return [doc_id for doc_id, _ in ordered[: self._per_path_top_k]]

    def _rrf_scores(self, rankings: list[list[str]]) -> dict[str, float]:
        """按 RRF 公式重算融合分，便于日志/测试读取，不改变排序逻辑。"""
        scores: dict[str, float] = {}
        for ranking in rankings:
            for rank, doc_id in enumerate(ranking, start=1):
                scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (self._k + rank)
        return scores


__all__ = ["FusionMode", "HybridRetriever"]
