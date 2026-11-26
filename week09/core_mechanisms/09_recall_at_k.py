"""
第 9 周 · 核心机制 09：Recall@K 看混合检索的收益
================================================================
【对应知识点】文档第 9 周验收：构造专名查询，对比纯向量 vs 混合

【周次学习要点】
  - Recall@K = 前 K 条命中相关文档数 / 相关文档总数；本周只看这一个轻量指标。
  - 同一批 query / 同一 K 下比较三路，才能把"召回差异"归因到检索方式。
  - 完整评测体系是第 12 周任务，这里只做最小可复现对比。

【易忽略细节】
  1. relevant 用 chunk_id 集合，避免整段文本比对带来的误判。
  2. K 必须固定；K=1 与 K=5 的结论常常不同，报告中要写清。
  3. 命中数为 0 时返回 0.0，不要因为分母为 0 就跳过这条 query。

【示例用途】可运行：`python -m week09.core_mechanisms.09_recall_at_k`
             测试见 tests/week09/test_core_mechanisms.py
"""
from __future__ import annotations

from collections.abc import Sequence
from typing import Literal

from week09.engineering.bm25_index import BM25Index
from week09.engineering.dense_index import DenseIndex
from week09.engineering.hybrid_retriever import HybridRetriever
from week09.engineering.models import Candidate

Method = Literal["bm25", "dense", "hybrid"]

CORPUS: list[Candidate] = [
    Candidate("r1", "SGCC-4012 断路器巡检周期与温度阈值", "manual"),
    Candidate("r2", "ERR_4012 错误码通信超时排查步骤", "error_codes"),
    Candidate("r3", "断路器巡检通用流程与注意事项", "manual"),
    Candidate("r4", "SGCC-5200 隔离开关检修周期", "manual"),
    Candidate("r5", "差旅报销与发票归档要求", "finance"),
    Candidate("r6", "SGCC-4012 客户投诉记录汇总", "crm"),
]

QUERIES: list[tuple[str, set[str]]] = [
    ("SGCC-4012 巡检周期", {"r1"}),
    ("ERR_4012 错误码", {"r2"}),
    ("断路器巡检注意事项", {"r3"}),
]


def recall_at_k(retrieved: Sequence[str], relevant: set[str], k: int) -> float:
    """单条查询的 Recall@K；无相关文档时按 0.0 计。"""
    if not relevant:
        return 0.0
    hits = len(set(retrieved[:k]) & relevant)
    return hits / len(relevant)


def evaluate(method: Method, k: int = 2) -> float:
    """在固定查询集上跑某一路，返回平均 Recall@K。"""
    scores: list[float] = []
    for query, relevant in QUERIES:
        if method == "bm25":
            retrieved = [doc_id for doc_id, _ in BM25Index(CORPUS).search(query, k)]
        elif method == "dense":
            retrieved = [doc_id for doc_id, _ in DenseIndex(CORPUS).search(query, k)]
        else:
            retrieved = [
                item.chunk_id
                for item in HybridRetriever(CORPUS).retrieve(query, top_k=k)
            ]
        scores.append(recall_at_k(retrieved, relevant, k))
    return sum(scores) / len(scores)


def demo() -> None:
    print(f"固定 K=2，共 {len(QUERIES)} 条查询（含专名与通用问题）")
    for method in ("bm25", "dense", "hybrid"):
        print(f"  {method:<7} Recall@2 = {evaluate(method):.3f}")
    print("专名 query 上 BM25 补位，通用 query 上向量补位 → 混合最稳")


if __name__ == "__main__":
    demo()
