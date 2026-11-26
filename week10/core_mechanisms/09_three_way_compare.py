"""
第 10 周 · 核心机制 09：纯向量 / 混合 / 混合+rerank 三方对比
================================================================
【对应知识点】文档第 10 周验收：三方指标对比

【周次学习要点】
  - 第三路只在前两路之上加二阶段精排，候选仍来自混合召回。
  - 三方共用同一批查询与同一个 K，才能把差异归因到模块。
  - 指标只做轻量 Recall@K；完整评测体系是第 12 周任务。

【易忽略细节】
  1. rerank 不能凭空找回被首阶段漏掉的文档 → 它的上限由混合召回决定。
  2. 候选转 RerankCandidate 时保留 stage_score，便于观察"降级前后"顺序。
  3. 教学语料小、查询少，数字只用于验证链路，不作为真实效果结论。

【示例用途】可运行：`python -m week10.core_mechanisms.09_three_way_compare`
             测试见 tests/week10/test_core_mechanisms.py
"""
from __future__ import annotations

from week09.engineering.dense_index import DenseIndex
from week09.engineering.hybrid_retriever import HybridRetriever
from week09.engineering.models import Candidate

from week10.engineering.models import RerankCandidate
from week10.engineering.reranker import DeterministicReranker

CORPUS: list[Candidate] = [
    Candidate("t1", "SGCC-4012 断路器巡检周期与温度阈值", "manual"),
    Candidate("t2", "SGCC-4012 型号说明书", "manual"),
    Candidate("t3", "ERR_4012 通信超时排查步骤", "error_codes"),
    Candidate("t4", "断路器通用巡检流程", "manual"),
    Candidate("t5", "差旅报销标准", "finance"),
]
QUERIES: list[tuple[str, frozenset[str]]] = [
    ("SGCC-4012 巡检周期", frozenset({"t1"})),
    ("ERR_4012 通信超时", frozenset({"t3"})),
    ("断路器巡检流程", frozenset({"t4"})),
]
RERANK_POOL = 10


def recall(retrieved: list[str], relevant: frozenset[str], k: int) -> float:
    """单条查询 Recall@K。"""
    if not relevant:
        return 0.0
    return len(set(retrieved[:k]) & set(relevant)) / len(relevant)


def three_way_compare(k: int = 2) -> dict[str, float]:
    """返回三路在固定查询集上的平均 Recall@K。"""
    retriever = HybridRetriever(CORPUS)
    reranker = DeterministicReranker()
    totals = {"dense": 0.0, "hybrid": 0.0, "hybrid_rerank": 0.0}
    for query, relevant in QUERIES:
        dense_ids = [doc_id for doc_id, _ in DenseIndex(CORPUS).search(query, k)]
        hybrid_items = retriever.retrieve(query, top_k=RERANK_POOL)
        hybrid_ids = [item.chunk_id for item in hybrid_items[:k]]
        rerank_input = [
            RerankCandidate(item.chunk_id, item.text, item.fused_score or 0.0)
            for item in hybrid_items
        ]
        pairs = [(item, reranker.score(query, item.text)) for item in rerank_input]
        ordered = sorted(pairs, key=lambda pair: (-pair[1], pair[0].chunk_id))
        rerank_ids = [item.chunk_id for item, _ in ordered[:k]]
        totals["dense"] += recall(dense_ids, relevant, k)
        totals["hybrid"] += recall(hybrid_ids, relevant, k)
        totals["hybrid_rerank"] += recall(rerank_ids, relevant, k)
    count = len(QUERIES)
    return {name: value / count for name, value in totals.items()}


def demo() -> None:
    result = three_way_compare()
    print(f"三方对比：{len(CORPUS)} 候选 / {len(QUERIES)} 查询 / Recall@2")
    for name, score in result.items():
        print(f"  {name:<15} {score:.3f}")
    print("rerank 只能重排已召回候选，不会补回首阶段漏掉的文档")


if __name__ == "__main__":
    demo()
